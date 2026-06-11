from __future__ import annotations

import json
import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from .models import ServiceConfig


DEFAULT_SERVICE_CONFIG = {
    "host": "127.0.0.1",
    "port": 9080,
    "check_config": "check_config.json",
    "daily_run_time": "02:00",
    "schedule_enabled": True,
    "schedule_weekdays": [0, 1, 2, 3, 4],
    "history_success_limit": 5,
    "history_failed_limit": 5,
    "ocr_archive_retention_days": 30,
    "reports_dir": "reports",
}


def _coerce_config(data: dict[str, object]) -> ServiceConfig:
    merged = dict(DEFAULT_SERVICE_CONFIG)
    merged.update(data)
    return ServiceConfig(
        host=str(merged["host"]),
        port=int(merged["port"]),
        check_config=str(merged["check_config"]),
        daily_run_time=str(merged["daily_run_time"]),
        schedule_enabled=bool(merged["schedule_enabled"]),
        schedule_weekdays=[int(value) for value in (merged["schedule_weekdays"] or [])],
        history_success_limit=int(merged["history_success_limit"]),
        history_failed_limit=int(merged["history_failed_limit"]),
        ocr_archive_retention_days=int(merged["ocr_archive_retention_days"]),
        reports_dir=str(merged["reports_dir"]),
    )


def load_or_create_config(path: Path) -> ServiceConfig:
    if not path.exists():
        config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
        save_config(path, config)
        return config
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("service config must be a JSON object")
    return _coerce_config(data)


def validate_config(config: ServiceConfig) -> list[str]:
    errors: list[str] = []
    if not re.fullmatch(r"\d{2}:\d{2}", config.daily_run_time):
        errors.append("daily_run_time must be HH:MM in 24-hour time")
    else:
        hour, minute = [int(part) for part in config.daily_run_time.split(":")]
        if hour > 23 or minute > 59:
            errors.append("daily_run_time must be HH:MM in 24-hour time")
    if config.history_success_limit <= 0:
        errors.append("history_success_limit must be a positive integer")
    if config.history_failed_limit <= 0:
        errors.append("history_failed_limit must be a positive integer")
    if config.ocr_archive_retention_days <= 0:
        errors.append("ocr_archive_retention_days must be a positive integer")
    if not config.reports_dir.strip():
        errors.append("reports_dir must not be empty")
    if config.port < 0 or config.port > 65535:
        errors.append("port must be between 0 and 65535")
    if not config.schedule_weekdays:
        errors.append("schedule_weekdays must include at least one weekday")
    elif any(day < 0 or day > 6 for day in config.schedule_weekdays):
        errors.append("schedule_weekdays values must be integers from 0 to 6")
    return errors


def save_config(path: Path, config: ServiceConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(config.to_dict(), ensure_ascii=False, indent=2)
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent)) as tmp:
        tmp.write(payload)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)
