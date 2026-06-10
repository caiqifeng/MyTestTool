import json
import os
import tempfile
import unittest
from pathlib import Path

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
