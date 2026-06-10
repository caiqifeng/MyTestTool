from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ServiceConfig:
    host: str
    port: int
    check_config: str
    daily_run_time: str
    history_success_limit: int
    history_failed_limit: int
    ocr_archive_retention_days: int
    reports_dir: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunMetadata:
    run_id: str
    trigger: str
    status: str
    started_at: str
    finished_at: str | None = None
    duration_seconds: float | None = None
    report_path: str | None = None
    log_path: str | None = None
    error_summary: str | None = None
    counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunMetadata":
        return cls(
            run_id=str(data["run_id"]),
            trigger=str(data["trigger"]),
            status=str(data["status"]),
            started_at=str(data["started_at"]),
            finished_at=data.get("finished_at"),
            duration_seconds=data.get("duration_seconds"),
            report_path=data.get("report_path"),
            log_path=data.get("log_path"),
            error_summary=data.get("error_summary"),
            counts=dict(data.get("counts") or {}),
        )
