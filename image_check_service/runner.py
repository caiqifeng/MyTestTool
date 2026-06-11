from __future__ import annotations

import contextlib
import datetime as dt
import io
import threading
import traceback
from pathlib import Path
from typing import Callable

import check_i18n_images

from .history import create_run_directory, record_failed_run, record_successful_run, write_metadata
from .models import RunMetadata, ServiceConfig


CheckCallable = Callable[[Path, Path], dict[str, int]]


def make_run_id(now: dt.datetime | None = None) -> str:
    return (now or dt.datetime.now()).strftime("%Y%m%d_%H%M%S_%f")


def _now_text() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")


class ReportRunner:
    def __init__(self, config: ServiceConfig, check_callable: CheckCallable | None = None):
        self.config = config
        self.check_callable = check_callable or self._run_existing_checker
        self._lock = threading.Lock()
        self._active_run_id: str | None = None
        self._active_metadata: RunMetadata | None = None

    @property
    def active_run_id(self) -> str | None:
        return self._active_run_id

    def active_run_snapshot(self) -> dict[str, object] | None:
        with self._lock:
            return self._active_metadata.to_dict() if self._active_metadata is not None else None

    def run_once(self, trigger: str) -> RunMetadata:
        with self._lock:
            if self._active_run_id is not None:
                raise RuntimeError(f"run already active: {self._active_run_id}")
            run_id = make_run_id()
            self._active_run_id = run_id
        try:
            return self._run_locked(run_id, trigger)
        finally:
            with self._lock:
                self._active_run_id = None
                self._active_metadata = None

    def _run_locked(self, run_id: str, trigger: str) -> RunMetadata:
        reports_dir = Path(self.config.reports_dir)
        run_dir = create_run_directory(reports_dir, run_id)
        report_path = run_dir / "ui_image_check_report.html"
        log_path = run_dir / "run.log"
        started = dt.datetime.now()
        metadata = RunMetadata(
            run_id=run_id,
            trigger=trigger,
            status="running",
            started_at=_now_text(),
            report_path=str(report_path),
            log_path=str(log_path),
        )
        with self._lock:
            self._active_metadata = metadata
        write_metadata(run_dir, metadata)

        try:
            counts = self.check_callable(report_path, log_path)
            finished = dt.datetime.now()
            metadata.status = "success"
            metadata.finished_at = _now_text()
            metadata.duration_seconds = (finished - started).total_seconds()
            metadata.counts = counts
            try:
                check_i18n_images.cleanup_ocr_cache_archive(
                    Path(check_i18n_images.OCR_CACHE_DB_FILE),
                    self.config.ocr_archive_retention_days,
                )
            except Exception as cleanup_error:
                with log_path.open("a", encoding="utf-8") as log:
                    log.write(f"\nWARN: OCR archive cleanup failed: {cleanup_error}\n")
            write_metadata(run_dir, metadata)
            record_successful_run(reports_dir, metadata, self.config.history_success_limit)
            return metadata
        except Exception as exc:
            finished = dt.datetime.now()
            metadata.status = "failed"
            metadata.finished_at = _now_text()
            metadata.duration_seconds = (finished - started).total_seconds()
            metadata.error_summary = str(exc)
            with log_path.open("a", encoding="utf-8") as log:
                log.write("\n")
                log.write(traceback.format_exc())
            write_metadata(run_dir, metadata)
            record_failed_run(reports_dir, metadata, self.config.history_failed_limit)
            return metadata

    def _run_existing_checker(self, output_path: Path, log_path: Path) -> dict[str, int]:
        args = [
            "--config",
            self.config.check_config,
            "--output",
            str(output_path),
        ]
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = check_i18n_images.main(args)
        log_path.write_text(stdout.getvalue() + stderr.getvalue(), encoding="utf-8")
        if exit_code != 0:
            raise RuntimeError(f"check_i18n_images exited with {exit_code}")
        return {}
