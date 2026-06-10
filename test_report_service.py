import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

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


class ReportServiceConfigTest(unittest.TestCase):
    def test_load_or_create_config_writes_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "report_service_config.json"

            config = load_or_create_config(path)

            self.assertIsInstance(config, ServiceConfig)
            self.assertEqual(config.daily_run_time, "02:00")
            self.assertEqual(config.history_success_limit, 5)
            self.assertTrue(path.exists())
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["reports_dir"], "reports")

    def test_validate_config_rejects_bad_time_and_non_positive_retention(self):
        config = ServiceConfig(
            host="127.0.0.1",
            port=9080,
            check_config="check_config.json",
            daily_run_time="25:99",
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
