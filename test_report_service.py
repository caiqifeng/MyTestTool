import json
import sqlite3
import urllib.error
import urllib.request
import os
import contextlib
import importlib
import io
import tempfile
import threading
import time
import unittest
import datetime as dt
from pathlib import Path
from unittest import mock

import check_i18n_images

from image_check_service.config import (
    DEFAULT_SERVICE_CONFIG,
    load_or_create_config,
    save_config,
    validate_config,
)
from image_check_service.history import (
    create_run_directory,
    load_index,
    record_failed_run,
    record_successful_run,
    write_metadata,
)
from image_check_service.models import RunMetadata, ServiceConfig
from image_check_service.runner import ReportRunner
from image_check_service.scheduler import DailyScheduler, next_daily_run
from image_check_service.web import build_console_html, create_server, status_payload


class ReportServiceConfigTest(unittest.TestCase):
    def test_load_or_create_config_writes_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "report_service_config.json"

            config = load_or_create_config(path)

            self.assertIsInstance(config, ServiceConfig)
            self.assertEqual(config.daily_run_time, "02:00")
            self.assertTrue(config.schedule_enabled)
            self.assertEqual(config.schedule_weekdays, [0, 1, 2, 3, 4])
            self.assertEqual(config.history_success_limit, 5)
            self.assertTrue(path.exists())
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["reports_dir"], "reports")
            self.assertTrue(raw["schedule_enabled"])
            self.assertEqual(raw["schedule_weekdays"], [0, 1, 2, 3, 4])

    def test_validate_config_rejects_bad_time_and_non_positive_retention(self):
        config = ServiceConfig(
            host="127.0.0.1",
            port=9080,
            check_config="check_config.json",
            daily_run_time="25:99",
            schedule_enabled=True,
            schedule_weekdays=[],
            history_success_limit=0,
            history_failed_limit=-1,
            ocr_archive_retention_days=0,
            reports_dir="reports",
        )

        errors = validate_config(config)

        self.assertIn("daily_run_time must be HH:MM in 24-hour time", errors)
        self.assertIn("history_success_limit must be a positive integer", errors)
        self.assertIn("history_failed_limit must be a positive integer", errors)
        self.assertIn("ocr_archive_retention_days must be a positive integer", errors)
        self.assertIn("schedule_weekdays must include at least one weekday", errors)

    def test_validate_config_rejects_weekdays_outside_monday_to_sunday(self):
        config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
        config.schedule_weekdays = [-1, 7]

        errors = validate_config(config)

        self.assertIn("schedule_weekdays values must be integers from 0 to 6", errors)

    def test_save_config_writes_json_atomically_readable(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "report_service_config.json"
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.daily_run_time = "03:30"

            save_config(path, config)
            loaded = load_or_create_config(path)

            self.assertEqual(loaded.daily_run_time, "03:30")


class ReportServiceHistoryTest(unittest.TestCase):
    def _metadata(self, run_id: str, status: str = "success") -> RunMetadata:
        return RunMetadata(
            run_id=run_id,
            trigger="manual",
            status=status,
            started_at=f"{run_id[:4]}-01-01 00:00:00 +0800",
            finished_at=f"{run_id[:4]}-01-01 00:01:00 +0800",
            report_path=f"reports/runs/{run_id}/ui_image_check_report.html",
            log_path=f"reports/runs/{run_id}/run.log",
        )

    def test_record_successful_run_updates_latest_and_retains_latest_five(self):
        with tempfile.TemporaryDirectory() as td:
            reports_dir = Path(td) / "reports"
            for i in range(6):
                run_id = f"20260610_02000{i}"
                run_dir = create_run_directory(reports_dir, run_id)
                (run_dir / "ui_image_check_report.html").write_text("ok", encoding="utf-8")
                assets = run_dir / "ui_image_check_report_assets"
                assets.mkdir()
                (assets / "old.png").write_bytes(b"png")
                meta = self._metadata(run_id)
                write_metadata(run_dir, meta)
                record_successful_run(reports_dir, meta, success_limit=5)

            index = load_index(reports_dir)

            self.assertEqual(index["latest_success_run_id"], "20260610_020005")
            self.assertEqual(len(index["successful_runs"]), 5)
            self.assertFalse((reports_dir / "runs" / "20260610_020000").exists())
            self.assertTrue((reports_dir / "runs" / "20260610_020005").exists())

    def test_record_failed_run_retains_failed_limit_without_touching_success(self):
        with tempfile.TemporaryDirectory() as td:
            reports_dir = Path(td) / "reports"
            success_dir = create_run_directory(reports_dir, "20260610_010000")
            success_meta = self._metadata("20260610_010000")
            write_metadata(success_dir, success_meta)
            record_successful_run(reports_dir, success_meta, success_limit=5)

            for i in range(3):
                run_id = f"20260610_03000{i}"
                failed_dir = create_run_directory(reports_dir, run_id)
                failed_meta = self._metadata(run_id, status="failed")
                failed_meta.error_summary = "boom"
                write_metadata(failed_dir, failed_meta)
                record_failed_run(reports_dir, failed_meta, failed_limit=2)

            index = load_index(reports_dir)

            self.assertEqual(index["latest_success_run_id"], "20260610_010000")
            self.assertEqual(len(index["failed_runs"]), 2)
            self.assertTrue((reports_dir / "runs" / "20260610_010000").exists())
            self.assertFalse((reports_dir / "runs" / "20260610_030000").exists())

    def test_record_successful_run_rejects_retention_when_runs_root_is_symlink(self):
        if not hasattr(os, "symlink"):
            self.skipTest("os.symlink is not available")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reports_dir = root / "reports"
            reports_dir.mkdir()
            external_runs = root / "external_runs"
            external_runs.mkdir()
            old_run_id = "20260610_020000"
            old_run_dir = external_runs / old_run_id
            old_run_dir.mkdir()
            (old_run_dir / "keep.txt").write_text("external data", encoding="utf-8")

            try:
                os.symlink(external_runs, reports_dir / "runs", target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"directory symlink is not available: {exc}")

            old_meta = self._metadata(old_run_id)
            (reports_dir / "index.json").write_text(
                json.dumps(
                    {
                        "latest_success_run_id": old_run_id,
                        "successful_runs": [old_meta.to_dict()],
                        "failed_runs": [],
                    }
                ),
                encoding="utf-8",
            )

            new_meta = self._metadata("20260610_020001")

            with self.assertRaises(ValueError):
                record_successful_run(reports_dir, new_meta, success_limit=1)

            self.assertTrue(old_run_dir.exists())
            self.assertTrue((old_run_dir / "keep.txt").exists())


class ReportServiceRunnerTest(unittest.TestCase):
    def test_runner_success_updates_latest_and_writes_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(root / "reports")
            config.check_config = str(root / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")

            def fake_check(output_path: Path, log_path: Path) -> dict[str, int]:
                output_path.write_text("<html>ok</html>", encoding="utf-8")
                (output_path.parent / "ui_image_check_report_assets").mkdir()
                log_path.write_text("ran", encoding="utf-8")
                return {"i18n_count": 1, "mainland_count": 1}

            with mock.patch("image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive") as cleanup:
                metadata = ReportRunner(config, check_callable=fake_check).run_once("manual")

            self.assertEqual(metadata.status, "success")
            self.assertEqual(metadata.counts["i18n_count"], 1)
            index = load_index(Path(config.reports_dir))
            self.assertEqual(index["latest_success_run_id"], metadata.run_id)
            self.assertTrue(Path(metadata.report_path).exists())
            cleanup.assert_called_once()
            self.assertEqual(cleanup.call_args.args[1], config.ocr_archive_retention_days)

    def test_runner_failure_does_not_replace_previous_latest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(root / "reports")
            config.check_config = str(root / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")

            def success(output_path: Path, log_path: Path) -> dict[str, int]:
                output_path.write_text("<html>ok</html>", encoding="utf-8")
                log_path.write_text("ok", encoding="utf-8")
                return {}

            with mock.patch("image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive"):
                runner = ReportRunner(config, check_callable=success)
                first = runner.run_once("manual")

            def failure(output_path: Path, log_path: Path) -> dict[str, int]:
                log_path.write_text("boom", encoding="utf-8")
                raise RuntimeError("boom")

            runner = ReportRunner(config, check_callable=failure)
            second = runner.run_once("manual")

            index = load_index(Path(config.reports_dir))
            self.assertEqual(first.status, "success")
            self.assertEqual(second.status, "failed")
            self.assertEqual(index["latest_success_run_id"], first.run_id)
            self.assertIn("boom", second.error_summary)

    def test_runner_cleanup_failure_keeps_success_and_logs_warning(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(root / "reports")
            config.check_config = str(root / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")

            def success(output_path: Path, log_path: Path) -> dict[str, int]:
                output_path.write_text("<html>ok</html>", encoding="utf-8")
                log_path.write_text("ok", encoding="utf-8")
                return {}

            with mock.patch("image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive"):
                first = ReportRunner(config, check_callable=success).run_once("manual")

            with mock.patch(
                "image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive",
                side_effect=RuntimeError("cleanup failed"),
            ):
                second = ReportRunner(config, check_callable=success).run_once("manual")

            index = load_index(Path(config.reports_dir))
            self.assertEqual(first.status, "success")
            self.assertEqual(second.status, "success")
            self.assertEqual(index["latest_success_run_id"], second.run_id)
            self.assertIn("cleanup failed", Path(second.log_path).read_text(encoding="utf-8"))

    def test_runner_prevents_concurrent_runs_and_releases_active_id(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            config.check_config = str(Path(td) / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")
            started = threading.Event()
            release = threading.Event()
            result: list[RunMetadata] = []

            def slow_check(output_path: Path, log_path: Path) -> dict[str, int]:
                started.set()
                release.wait(timeout=5)
                output_path.write_text("<html>ok</html>", encoding="utf-8")
                log_path.write_text("ok", encoding="utf-8")
                return {}

            runner = ReportRunner(config, check_callable=slow_check)
            with mock.patch("image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive"):
                thread = threading.Thread(target=lambda: result.append(runner.run_once("manual")))
                thread.start()
                self.assertTrue(started.wait(timeout=5))
                active_id = runner.active_run_id
                self.assertIsNotNone(active_id)

                with self.assertRaises(RuntimeError) as ctx:
                    runner.run_once("manual")

                self.assertIn(str(active_id), str(ctx.exception))
                release.set()
                thread.join(timeout=5)

            self.assertFalse(thread.is_alive())
            self.assertIsNone(runner.active_run_id)
            self.assertEqual(result[0].status, "success")

    def test_runner_exposes_active_run_snapshot_while_running(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            config.check_config = str(Path(td) / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")
            started = threading.Event()
            release = threading.Event()

            def slow_check(output_path: Path, log_path: Path) -> dict[str, int]:
                log_path.write_text("step 1\n", encoding="utf-8")
                started.set()
                release.wait(timeout=5)
                output_path.write_text("<html>ok</html>", encoding="utf-8")
                return {"findings": 1}

            runner = ReportRunner(config, check_callable=slow_check)
            with mock.patch("image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive"):
                thread = threading.Thread(target=lambda: runner.run_once("manual"))
                thread.start()
                self.assertTrue(started.wait(timeout=5))

                snapshot = runner.active_run_snapshot()

                self.assertIsNotNone(snapshot)
                self.assertEqual(snapshot["status"], "running")
                self.assertEqual(snapshot["trigger"], "manual")
                self.assertTrue(Path(str(snapshot["log_path"])).exists())
                self.assertIn("step 1", Path(str(snapshot["log_path"])).read_text(encoding="utf-8"))
                release.set()
                thread.join(timeout=5)

            self.assertFalse(thread.is_alive())
            self.assertIsNone(runner.active_run_snapshot())

    def test_runner_releases_active_id_after_check_failure(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            config.check_config = str(Path(td) / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")

            def failure(output_path: Path, log_path: Path) -> dict[str, int]:
                raise RuntimeError("boom")

            runner = ReportRunner(config, check_callable=failure)

            metadata = runner.run_once("manual")

            self.assertEqual(metadata.status, "failed")
            self.assertIsNone(runner.active_run_id)

    def test_default_checker_captures_stdout_and_stderr(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            config.check_config = str(Path(td) / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")
            runner = ReportRunner(config, check_callable=lambda output, log: {})

            def fake_main(args: list[str]) -> int:
                print("stdout message")
                print("stderr message", file=__import__("sys").stderr)
                return 0

            log_path = Path(td) / "run.log"
            with mock.patch("image_check_service.runner.check_i18n_images.main", side_effect=fake_main):
                counts = runner._run_existing_checker(Path(td) / "report.html", log_path)

            log_text = log_path.read_text(encoding="utf-8")
            self.assertEqual(counts, {})
            self.assertIn("stdout message", log_text)
            self.assertIn("stderr message", log_text)

    def test_default_checker_streams_stdout_to_log_while_running(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            config.check_config = str(Path(td) / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")
            runner = ReportRunner(config, check_callable=lambda output, log: {})
            printed = threading.Event()
            release = threading.Event()

            def fake_main(args: list[str]) -> int:
                print("live progress line")
                printed.set()
                release.wait(timeout=5)
                return 0

            log_path = Path(td) / "run.log"
            with mock.patch("image_check_service.runner.check_i18n_images.main", side_effect=fake_main):
                thread = threading.Thread(target=lambda: runner._run_existing_checker(Path(td) / "report.html", log_path))
                thread.start()
                self.assertTrue(printed.wait(timeout=5))
                try:
                    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
                finally:
                    release.set()
                    thread.join(timeout=5)

            self.assertFalse(thread.is_alive())
            self.assertIn("live progress line", log_text)


class ReportServiceSchedulerTest(unittest.TestCase):
    def test_next_daily_run_returns_today_when_time_is_future(self):
        now = dt.datetime(2026, 6, 10, 1, 30)

        result = next_daily_run("02:00", now)

        self.assertEqual(result, dt.datetime(2026, 6, 10, 2, 0))

    def test_next_daily_run_returns_tomorrow_when_time_has_passed(self):
        now = dt.datetime(2026, 6, 10, 3, 0)

        result = next_daily_run("02:00", now)

        self.assertEqual(result, dt.datetime(2026, 6, 11, 2, 0))

    def test_next_daily_run_returns_tomorrow_when_time_equals_now(self):
        now = dt.datetime(2026, 6, 10, 2, 0)

        result = next_daily_run("02:00", now)

        self.assertEqual(result, dt.datetime(2026, 6, 11, 2, 0))

    def test_next_daily_run_returns_none_when_schedule_disabled(self):
        now = dt.datetime(2026, 6, 10, 1, 30)

        result = next_daily_run("02:00", now, enabled=False)

        self.assertIsNone(result)

    def test_next_daily_run_skips_to_next_allowed_weekday(self):
        now = dt.datetime(2026, 6, 10, 1, 30)  # Wednesday

        result = next_daily_run("02:00", now, weekdays=[4])

        self.assertEqual(result, dt.datetime(2026, 6, 12, 2, 0))

    def test_scheduler_start_is_idempotent_and_stop_returns(self):
        scheduler = DailyScheduler(
            get_daily_run_time=lambda: "23:59",
            run_scheduled=lambda: None,
            poll_seconds=0.01,
        )

        scheduler.start()
        first_thread = scheduler._thread
        scheduler.start()

        self.assertIs(scheduler._thread, first_thread)
        self.assertIsNotNone(scheduler.next_run)
        scheduler.stop()
        self.assertFalse(first_thread.is_alive())

    def test_scheduler_stop_interrupts_long_poll_sleep(self):
        scheduler = DailyScheduler(
            get_daily_run_time=lambda: "23:59",
            run_scheduled=lambda: None,
            poll_seconds=5.0,
        )

        scheduler.start()
        self.assertIsNotNone(scheduler._thread)
        scheduler.stop()

        self.assertFalse(scheduler._thread.is_alive())

    def test_scheduler_runs_when_due(self):
        called = threading.Event()
        current = dt.datetime(2026, 6, 10, 2, 0)
        now_values = [current, dt.datetime(2026, 6, 10, 2, 1)]
        scheduler = DailyScheduler(
            get_daily_run_time=lambda: "02:01",
            run_scheduled=lambda: called.set(),
            poll_seconds=0.01,
            now_provider=lambda: now_values.pop(0) if now_values else dt.datetime(2026, 6, 10, 2, 1),
        )

        scheduler.start()
        self.assertTrue(called.wait(timeout=2))
        scheduler.stop()

    def test_scheduler_survives_run_and_error_handler_exceptions(self):
        calls = 0
        errors: list[str] = []
        now_values = [
            dt.datetime(2026, 6, 10, 2, 0),
            dt.datetime(2026, 6, 10, 2, 1),
            dt.datetime(2026, 6, 11, 2, 0),
            dt.datetime(2026, 6, 11, 2, 1),
        ]

        def run_scheduled() -> None:
            nonlocal calls
            calls += 1
            raise RuntimeError("scheduled failure")

        def error_handler(exc: BaseException, formatted: str) -> None:
            errors.append(str(exc))
            raise RuntimeError("handler failure")

        scheduler = DailyScheduler(
            get_daily_run_time=lambda: "02:01",
            run_scheduled=run_scheduled,
            poll_seconds=0.01,
            error_handler=error_handler,
            now_provider=lambda: now_values.pop(0) if now_values else dt.datetime(2026, 6, 11, 2, 1),
        )

        scheduler.start()
        deadline = dt.datetime.now() + dt.timedelta(seconds=2)
        while calls < 2 and dt.datetime.now() < deadline:
            time.sleep(0.01)
        scheduler.stop()

        self.assertGreaterEqual(calls, 2)
        self.assertIn("scheduled failure", errors)


class ReportServiceWebTest(unittest.TestCase):
    def _request_json(self, url: str, method: str = "GET", data: dict[str, object] | None = None):
        body = None if data is None else json.dumps(data).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                payload = response.read().decode("utf-8")
                return response.status, json.loads(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read().decode("utf-8")
            return exc.code, json.loads(payload)

    def test_status_payload_includes_latest_and_config_errors(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            payload = status_payload(
                config,
                active_run_id=None,
                next_run_text="2026-06-11 02:00:00",
                config_errors=["bad"],
            )

            self.assertEqual(payload["status"], "idle")
            self.assertEqual(payload["next_scheduled_run"], "2026-06-11 02:00:00")
            self.assertEqual(payload["config_errors"], ["bad"])
            self.assertIn("latest_success_run_id", payload)
            self.assertTrue(payload["config"]["schedule_enabled"])
            self.assertEqual(payload["config"]["schedule_weekdays"], [0, 1, 2, 3, 4])

    def test_console_html_contains_required_controls(self):
        html = build_console_html()

        self.assertIn("ART SCANNER", html)
        self.assertIn("最新结果", html)
        self.assertIn("任务管理", html)
        self.assertIn("历史记录", html)
        self.assertIn("定时设置", html)
        self.assertIn("latestReportFrame", html)
        self.assertIn('id="view-latest"', html)
        self.assertIn('id="view-history"', html)
        self.assertIn('id="view-settings"', html)
        self.assertIn("historyRows", html)
        self.assertIn("historyTrend", html)
        self.assertIn("activeRunId", html)
        self.assertIn("activeRunLog", html)
        self.assertIn("schedule_enabled", html)
        self.assertIn("schedule_weekdays", html)
        self.assertIn("runNow", html)
        self.assertIn("daily_run_time", html)
        self.assertIn("打开最新报告", html)
        self.assertIn("/api/status", html)
        self.assertIn("/api/runs", html)

    def test_http_status_and_manual_run(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.host = "127.0.0.1"
            config.port = 0
            config.reports_dir = str(root / "reports")
            config_path = root / "service.json"

            def fake_check(output_path: Path, log_path: Path) -> dict[str, int]:
                output_path.write_text("<html>ok</html>", encoding="utf-8")
                log_path.write_text("ok", encoding="utf-8")
                return {"total": 1}

            runner = ReportRunner(config, check_callable=fake_check)
            with mock.patch("image_check_service.runner.check_i18n_images.cleanup_ocr_cache_archive"):
                server = create_server(config, config_path, runner, lambda: "2026-06-11 02:00:00")
                config.port = server.server_address[1]
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base_url = f"http://127.0.0.1:{server.server_address[1]}"
                try:
                    status, payload = self._request_json(f"{base_url}/api/status")
                    self.assertEqual(status, 200)
                    self.assertEqual(payload["status"], "idle")

                    status, payload = self._request_json(f"{base_url}/api/runs", method="POST")
                    self.assertEqual(status, 202)
                    self.assertTrue(payload["ok"])

                    status, payload = self._request_json(f"{base_url}/api/status")
                    self.assertEqual(status, 200)
                    self.assertEqual(payload["latest_success_run_id"], payload["successful_runs"][0]["run_id"])
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=5)

    def test_http_config_rejects_invalid_without_mutating_current_config(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.host = "127.0.0.1"
            config.port = 0
            config.reports_dir = str(root / "reports")
            config_path = root / "service.json"
            runner = ReportRunner(config, check_callable=lambda output, log: {})
            server = create_server(config, config_path, runner, lambda: None)
            config.port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                status, payload = self._request_json(
                    f"{base_url}/api/config",
                    method="POST",
                    data={"daily_run_time": "99:99"},
                )

                self.assertEqual(status, 400)
                self.assertFalse(payload["ok"])
                self.assertEqual(config.daily_run_time, "02:00")
                self.assertFalse(config_path.exists())

                status, payload = self._request_json(
                    f"{base_url}/api/config",
                    method="POST",
                    data={
                        "daily_run_time": "03:30",
                        "history_success_limit": 7,
                        "schedule_enabled": False,
                        "schedule_weekdays": [1, 3, 5],
                    },
                )

                self.assertEqual(status, 200)
                self.assertTrue(payload["ok"])
                self.assertEqual(config.daily_run_time, "03:30")
                self.assertEqual(config.history_success_limit, 7)
                self.assertFalse(config.schedule_enabled)
                self.assertEqual(config.schedule_weekdays, [1, 3, 5])
                self.assertTrue(config_path.exists())
                saved = json.loads(config_path.read_text(encoding="utf-8"))
                self.assertFalse(saved["schedule_enabled"])
                self.assertEqual(saved["schedule_weekdays"], [1, 3, 5])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_http_ocr_operation_accepts_report_payload_and_writes_sqlite_cache(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.host = "127.0.0.1"
            config.port = 0
            config.reports_dir = str(root / "reports")
            runner = ReportRunner(config, check_callable=lambda output, log: {})
            server = create_server(config, root / "service.json", runner, lambda: None)
            config.port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                with mock.patch("image_check_service.web.check_i18n_images.OCR_CACHE_DB_FILE", str(root / ".ocr_cache.db")):
                    status, payload = self._request_json(
                        f"{base_url}/api/ocr-cache/operation",
                        method="POST",
                        data={"relativePath": "a/b.png", "md5": "abc", "operation": "ignore"},
                    )

                self.assertEqual(status, 200)
                self.assertTrue(payload["ok"])
                conn = sqlite3.connect(root / ".ocr_cache.db")
                try:
                    row = conn.execute(
                        "SELECT md5, operation FROM ocr_cache WHERE relative_path=?",
                        ("a/b.png",),
                    ).fetchone()
                finally:
                    conn.close()
                self.assertEqual(row, ("abc", "ignore"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_http_ocr_operation_accepts_nested_report_path_payload(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.host = "127.0.0.1"
            config.port = 0
            config.reports_dir = str(root / "reports")
            runner = ReportRunner(config, check_callable=lambda output, log: {})
            server = create_server(config, root / "service.json", runner, lambda: None)
            config.port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                with mock.patch("image_check_service.web.check_i18n_images.OCR_CACHE_DB_FILE", str(root / ".ocr_cache.db")):
                    status, payload = self._request_json(
                        f"{base_url}/reports/runs/run1/api/ocr-cache/operation",
                        method="POST",
                        data={"relativePath": "a/b.png", "md5": "abc", "operation": ""},
                    )

                self.assertEqual(status, 200)
                self.assertTrue(payload["ok"])
                conn = sqlite3.connect(root / ".ocr_cache.db")
                try:
                    row = conn.execute(
                        "SELECT md5, operation FROM ocr_cache WHERE relative_path=?",
                        ("a/b.png",),
                    ).fetchone()
                finally:
                    conn.close()
                self.assertEqual(row, ("abc", ""))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_http_reports_serves_files_and_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reports_dir = root / "reports"
            report = reports_dir / "runs" / "run1" / "ui_image_check_report.html"
            report.parent.mkdir(parents=True)
            report.write_text("<html>report</html>", encoding="utf-8")
            (root / "secret.txt").write_text("secret", encoding="utf-8")
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.host = "127.0.0.1"
            config.port = 0
            config.reports_dir = str(reports_dir)
            runner = ReportRunner(config, check_callable=lambda output, log: {})
            server = create_server(config, root / "service.json", runner, lambda: None)
            config.port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                with urllib.request.urlopen(f"{base_url}/reports/runs/run1/ui_image_check_report.html", timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn("report", response.read().decode("utf-8"))

                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(f"{base_url}/reports/../secret.txt", timeout=5)
                self.assertEqual(ctx.exception.code, 404)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_http_run_log_endpoint_serves_recent_log_text(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reports_dir = root / "reports"
            log_path = reports_dir / "runs" / "run1" / "run.log"
            log_path.parent.mkdir(parents=True)
            log_path.write_text("line 1\nline 2\n", encoding="utf-8")
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.host = "127.0.0.1"
            config.port = 0
            config.reports_dir = str(reports_dir)
            runner = ReportRunner(config, check_callable=lambda output, log: {})
            server = create_server(config, root / "service.json", runner, lambda: None)
            config.port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                status, payload = self._request_json(f"{base_url}/reports/runs/run1/api/log")

                self.assertEqual(status, 200)
                self.assertEqual(payload["run_id"], "run1")
                self.assertIn("line 2", payload["log"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


class ReportServiceEntrypointTest(unittest.TestCase):
    def test_parse_args_uses_default_config_and_no_browser_flag(self):
        report_service = importlib.import_module("report_service")

        args = report_service.parse_args(["--no-browser"])

        self.assertEqual(args.config, "report_service_config.json")
        self.assertTrue(args.no_browser)

    def test_build_service_components_loads_config_and_constructs_components(self):
        report_service = importlib.import_module("report_service")
        with tempfile.TemporaryDirectory() as td:
            config_path = Path(td) / "service.json"
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.port = 0
            config.reports_dir = str(Path(td) / "reports")
            save_config(config_path, config)

            loaded, runner, scheduler, server = report_service.build_service_components(config_path)

            try:
                self.assertEqual(loaded.reports_dir, config.reports_dir)
                self.assertIsNotNone(runner)
                self.assertIsNotNone(scheduler)
                self.assertIsNotNone(server)
            finally:
                server.server_close()

    def test_build_service_components_rejects_invalid_config(self):
        report_service = importlib.import_module("report_service")
        with tempfile.TemporaryDirectory() as td:
            config_path = Path(td) / "service.json"
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.daily_run_time = "99:99"
            save_config(config_path, config)

            with self.assertRaises(ValueError):
                report_service.build_service_components(config_path)

    def test_main_stops_scheduler_and_closes_server_on_keyboard_interrupt(self):
        report_service = importlib.import_module("report_service")
        config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
        config.host = "127.0.0.1"
        config.port = 12345
        scheduler = mock.Mock()
        server = mock.Mock()
        server.server_address = ("127.0.0.1", 12345)
        server.serve_forever.side_effect = KeyboardInterrupt

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), mock.patch.object(
            report_service,
            "build_service_components",
            return_value=(config, mock.Mock(), scheduler, server),
        ), mock.patch.object(report_service.webbrowser, "open"):
            exit_code = report_service.main(["--no-browser"])

        self.assertEqual(exit_code, 0)
        scheduler.start.assert_called_once()
        server.serve_forever.assert_called_once()
        scheduler.stop.assert_called_once()
        server.server_close.assert_called_once()

    def test_main_returns_nonzero_when_config_is_invalid(self):
        report_service = importlib.import_module("report_service")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), mock.patch.object(
            report_service,
            "build_service_components",
            side_effect=ValueError("Service config has errors:\n- bad"),
        ) as build_components:
            exit_code = report_service.main(["--no-browser"])

        self.assertEqual(exit_code, 2)
        self.assertIn("Service config has errors", stdout.getvalue())
        build_components.assert_called_once()
