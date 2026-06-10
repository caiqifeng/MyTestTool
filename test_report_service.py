import json
import tempfile
import unittest
from pathlib import Path

from image_check_service.config import (
    DEFAULT_SERVICE_CONFIG,
    load_or_create_config,
    save_config,
    validate_config,
)
from image_check_service.models import ServiceConfig


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
