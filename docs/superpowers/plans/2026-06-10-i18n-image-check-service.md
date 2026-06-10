# I18n Image Check Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a persistent local management service for `check_i18n_images.py` with manual runs, daily scheduled runs, report history retention, safe report asset cleanup, and OCR stale-MD5 archival.

**Architecture:** Add focused service modules under `image_check_service/` and a thin `report_service.py` entrypoint. Keep `check_i18n_images.py` as the scan/report engine, adding only OCR archive helpers needed by the service. Store service-owned reports under `reports/` and never delete configured source image directories.

**Tech Stack:** Python standard library (`http.server`, `threading`, `sqlite3`, `json`, `subprocess` or direct callable runner), existing `unittest` test style, existing `check_i18n_images.py` functions.

---

## File Structure

- Create `image_check_service/__init__.py`
  - Package marker.
- Create `image_check_service/config.py`
  - Load, create, validate, and save `report_service_config.json`.
- Create `image_check_service/models.py`
  - Dataclasses for `ServiceConfig`, `RunMetadata`, `RunIndex`, and status helpers.
- Create `image_check_service/history.py`
  - Run directory creation, metadata read/write, `reports/index.json`, success/failed retention, safe service-owned cleanup.
- Create `image_check_service/scheduler.py`
  - Daily `HH:MM` next-run calculation and scheduler loop.
- Create `image_check_service/runner.py`
  - Single-run orchestration around existing checker, active-run lock, success/failure metadata, latest pointer update, cleanup hooks.
- Create `image_check_service/web.py`
  - HTTP server, console page, JSON APIs, static report serving, OCR ignore operation endpoint.
- Create `report_service.py`
  - CLI entrypoint for the management service.
- Create `test_report_service.py`
  - Service module tests using `unittest` and temporary directories.
- Modify `check_i18n_images.py`
  - Add OCR archive table initialization.
  - Add stale MD5 archive-on-replace helper.
  - Add archive retention cleanup helper.
  - Preserve existing lookup semantics and ignore operation semantics.
- Modify `test_check_i18n_images.py`
  - Add tests for OCR stale MD5 archival, retention deletion, and ignore-by-current-MD5 behavior.

## Task 1: Service Config Module

**Files:**
- Create: `image_check_service/__init__.py`
- Create: `image_check_service/models.py`
- Create: `image_check_service/config.py`
- Test: `test_report_service.py`

- [ ] **Step 1: Add failing config tests**

Append this to new `test_report_service.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m unittest test_report_service.ReportServiceConfigTest -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'image_check_service'`.

- [ ] **Step 3: Create package and config implementation**

Create `image_check_service/__init__.py`:

```python
"""Management service for the i18n image check workflow."""
```

Create `image_check_service/models.py`:

```python
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
```

Create `image_check_service/config.py`:

```python
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
    if config.port <= 0 or config.port > 65535:
        errors.append("port must be between 1 and 65535")
    return errors


def save_config(path: Path, config: ServiceConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(config.to_dict(), ensure_ascii=False, indent=2)
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent)) as tmp:
        tmp.write(payload)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)
```

- [ ] **Step 4: Run config tests**

Run:

```powershell
python -m unittest test_report_service.ReportServiceConfigTest -v
```

Expected: PASS, 3 tests.

- [ ] **Step 5: Commit**

```powershell
git add image_check_service/__init__.py image_check_service/models.py image_check_service/config.py test_report_service.py
git commit -m "feat: add report service config"
```

## Task 2: Run History and Safe Cleanup

**Files:**
- Modify: `image_check_service/models.py`
- Create: `image_check_service/history.py`
- Test: `test_report_service.py`

- [ ] **Step 1: Add failing history tests**

Append to `test_report_service.py`:

```python
from image_check_service.history import (
    create_run_directory,
    load_index,
    record_failed_run,
    record_successful_run,
    write_metadata,
)
from image_check_service.models import RunMetadata


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
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m unittest test_report_service.ReportServiceHistoryTest -v
```

Expected: FAIL with `ModuleNotFoundError` or missing history functions.

- [ ] **Step 3: Implement history module**

Create `image_check_service/history.py`:

```python
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .models import RunMetadata


INDEX_NAME = "index.json"


def _default_index() -> dict[str, object]:
    return {
        "latest_success_run_id": None,
        "successful_runs": [],
        "failed_runs": [],
    }


def load_index(reports_dir: Path) -> dict[str, object]:
    path = reports_dir / INDEX_NAME
    if not path.exists():
        return _default_index()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return _default_index()
    index = _default_index()
    index.update(data)
    index["successful_runs"] = list(index.get("successful_runs") or [])
    index["failed_runs"] = list(index.get("failed_runs") or [])
    return index


def save_index(reports_dir: Path, index: dict[str, object]) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / INDEX_NAME).write_text(
        json.dumps(index, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def create_run_directory(reports_dir: Path, run_id: str) -> Path:
    run_dir = reports_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_metadata(run_dir: Path, metadata: RunMetadata) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def read_metadata(run_dir: Path) -> RunMetadata:
    data = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    return RunMetadata.from_dict(data)


def _delete_service_run_dir(reports_dir: Path, run_id: str) -> None:
    target = (reports_dir / "runs" / run_id).resolve()
    allowed_root = (reports_dir / "runs").resolve()
    if allowed_root not in target.parents:
        raise ValueError(f"refusing to delete outside service run root: {target}")
    if target.exists():
        shutil.rmtree(target)


def _trim_runs(reports_dir: Path, runs: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    sorted_runs = sorted(runs, key=lambda item: str(item.get("run_id", "")), reverse=True)
    keep = sorted_runs[:limit]
    remove = sorted_runs[limit:]
    for item in remove:
        run_id = str(item.get("run_id", ""))
        if run_id:
            _delete_service_run_dir(reports_dir, run_id)
    return keep


def record_successful_run(reports_dir: Path, metadata: RunMetadata, success_limit: int) -> None:
    index = load_index(reports_dir)
    runs = [item for item in index["successful_runs"] if item.get("run_id") != metadata.run_id]
    runs.append(metadata.to_dict())
    index["latest_success_run_id"] = metadata.run_id
    index["successful_runs"] = _trim_runs(reports_dir, runs, success_limit)
    save_index(reports_dir, index)


def record_failed_run(reports_dir: Path, metadata: RunMetadata, failed_limit: int) -> None:
    index = load_index(reports_dir)
    runs = [item for item in index["failed_runs"] if item.get("run_id") != metadata.run_id]
    runs.append(metadata.to_dict())
    index["failed_runs"] = _trim_runs(reports_dir, runs, failed_limit)
    save_index(reports_dir, index)
```

- [ ] **Step 4: Run history tests**

Run:

```powershell
python -m unittest test_report_service.ReportServiceHistoryTest -v
```

Expected: PASS, 2 tests.

- [ ] **Step 5: Run config and history tests together**

Run:

```powershell
python -m unittest test_report_service -v
```

Expected: PASS, 5 tests.

- [ ] **Step 6: Commit**

```powershell
git add image_check_service/models.py image_check_service/history.py test_report_service.py
git commit -m "feat: add report run history"
```

## Task 3: OCR Archive Lifecycle

**Files:**
- Modify: `check_i18n_images.py`
- Modify: `test_check_i18n_images.py`

- [ ] **Step 1: Add failing OCR archive tests**

Add these tests near existing OCR cache tests in `test_check_i18n_images.py`:

```python
    def test_sqlite_cache_archives_old_md5_when_same_path_changes(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "cache.db"
            init_ocr_cache_db(db)
            conn = sqlite3.connect(db)
            try:
                conn.execute(
                    """
                    INSERT INTO ocr_cache(relative_path, md5, has_text, has_cn, test_str, operation, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("ui/a.tga", "old-md5", 1, 1, cn(r"\u65e7\u56fe"), "ignore", "2026-06-01 00:00:00 +0800"),
                )
                conn.commit()
            finally:
                conn.close()

            archive_stale_ocr_entry(db, "ui/a.tga", "new-md5", now_text="2026-06-10 00:00:00 +0800")

            conn = sqlite3.connect(db)
            try:
                archived = conn.execute(
                    "SELECT relative_path, md5, test_str, operation, archived_at FROM ocr_cache_archive"
                ).fetchone()
            finally:
                conn.close()

            self.assertEqual(archived, ("ui/a.tga", "old-md5", cn(r"\u65e7\u56fe"), "ignore", "2026-06-10 00:00:00 +0800"))

    def test_cleanup_ocr_archive_deletes_records_older_than_retention(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "cache.db"
            init_ocr_cache_db(db)
            conn = sqlite3.connect(db)
            try:
                conn.execute(
                    """
                    INSERT INTO ocr_cache_archive(relative_path, md5, has_text, has_cn, test_str, operation, updated_at, archived_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("old.tga", "old", 1, 1, "old", None, "2026-01-01 00:00:00 +0800", "2026-01-01 00:00:00 +0800"),
                )
                conn.execute(
                    """
                    INSERT INTO ocr_cache_archive(relative_path, md5, has_text, has_cn, test_str, operation, updated_at, archived_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("new.tga", "new", 1, 1, "new", None, "2026-06-09 00:00:00 +0800", "2026-06-09 00:00:00 +0800"),
                )
                conn.commit()
            finally:
                conn.close()

            deleted = cleanup_ocr_cache_archive(db, retention_days=30, now=dt.datetime(2026, 6, 10, tzinfo=BEIJING_TZ))

            conn = sqlite3.connect(db)
            try:
                remaining = conn.execute("SELECT relative_path FROM ocr_cache_archive ORDER BY relative_path").fetchall()
            finally:
                conn.close()
            self.assertEqual(deleted, 1)
            self.assertEqual(remaining, [("new.tga",)])
```

Also add imports at the top:

```python
import sqlite3
from check_i18n_images import (
    BEIJING_TZ,
    archive_stale_ocr_entry,
    cleanup_ocr_cache_archive,
)
```

If `BEIJING_TZ` is already available through wildcard edits, keep a single import list and avoid duplicates.

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m unittest test_check_i18n_images.CheckI18nImagesTest.test_sqlite_cache_archives_old_md5_when_same_path_changes test_check_i18n_images.CheckI18nImagesTest.test_cleanup_ocr_archive_deletes_records_older_than_retention -v
```

Expected: FAIL because `archive_stale_ocr_entry` and `cleanup_ocr_cache_archive` are undefined.

- [ ] **Step 3: Add archive table and helpers**

Modify `check_i18n_images.py`:

1. In `init_ocr_cache_db`, after `review_operation` table creation, add:

```python
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ocr_cache_archive (
                relative_path TEXT NOT NULL,
                md5 TEXT NOT NULL,
                has_text INTEGER,
                has_cn INTEGER,
                test_str TEXT,
                operation TEXT,
                updated_at TEXT NOT NULL,
                archived_at TEXT NOT NULL,
                PRIMARY KEY(relative_path, md5, archived_at)
            )
            """
        )
```

2. Add helpers after `_now_text()`:

```python
def archive_stale_ocr_entry(
    db_path: Path,
    relative_path: str,
    new_md5: str,
    now_text: str | None = None,
) -> bool:
    init_ocr_cache_db(db_path)
    archived_at = now_text or _now_text()
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            """
            SELECT relative_path, md5, has_text, has_cn, test_str, operation, updated_at
            FROM ocr_cache
            WHERE relative_path=? AND md5<>?
            """,
            (relative_path, new_md5),
        ).fetchone()
        if row is None:
            return False
        conn.execute(
            """
            INSERT OR IGNORE INTO ocr_cache_archive(
                relative_path, md5, has_text, has_cn, test_str, operation, updated_at, archived_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*row, archived_at),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def cleanup_ocr_cache_archive(
    db_path: Path,
    retention_days: int,
    now: dt.datetime | None = None,
) -> int:
    init_ocr_cache_db(db_path)
    current = now or dt.datetime.now(BEIJING_TZ)
    if current.tzinfo is None:
        current = current.replace(tzinfo=BEIJING_TZ)
    cutoff = current - dt.timedelta(days=retention_days)
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT rowid, archived_at FROM ocr_cache_archive").fetchall()
        delete_ids: list[int] = []
        for rowid, archived_at in rows:
            try:
                archived = dt.datetime.strptime(str(archived_at), "%Y-%m-%d %H:%M:%S %z")
            except ValueError:
                continue
            if archived < cutoff:
                delete_ids.append(int(rowid))
        for rowid in delete_ids:
            conn.execute("DELETE FROM ocr_cache_archive WHERE rowid=?", (rowid,))
        conn.commit()
        return len(delete_ids)
    finally:
        conn.close()
```

- [ ] **Step 4: Archive before replacing active cache rows**

In `sqlite_ocr_text_detector_factory.detect`, before the `INSERT INTO ocr_cache(...)` statement, add:

```python
                archive_stale_ocr_entry(db_path, image.relative_path, file_md5, now_text=now_text)
```

In `update_ocr_cache_operation_sqlite`, before inserting into `ocr_cache`, add:

```python
        archive_stale_ocr_entry(db_path, relative_path, file_md5, now_text=now_text)
```

If this creates nested DB initialization but tests pass, keep it simple for this feature. If SQLite locking occurs, refactor helper to accept an existing connection in a later step.

- [ ] **Step 5: Run OCR archive tests**

Run:

```powershell
python -m unittest test_check_i18n_images.CheckI18nImagesTest.test_sqlite_cache_archives_old_md5_when_same_path_changes test_check_i18n_images.CheckI18nImagesTest.test_cleanup_ocr_archive_deletes_records_older_than_retention -v
```

Expected: PASS, 2 tests.

- [ ] **Step 6: Run full image-check test file**

Run:

```powershell
python -m unittest test_check_i18n_images -v
```

Expected: PASS or existing environment-dependent skips only. If failures are unrelated to OCR archive changes, capture exact failing tests before continuing.

- [ ] **Step 7: Commit**

```powershell
git add check_i18n_images.py test_check_i18n_images.py
git commit -m "feat: archive stale ocr cache entries"
```

## Task 4: Runner Orchestration

**Files:**
- Create: `image_check_service/runner.py`
- Modify: `test_report_service.py`

- [ ] **Step 1: Add failing runner tests**

Append to `test_report_service.py`:

```python
from image_check_service.runner import ReportRunner


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

            runner = ReportRunner(config, check_callable=fake_check)
            metadata = runner.run_once("manual")

            self.assertEqual(metadata.status, "success")
            self.assertEqual(metadata.counts["i18n_count"], 1)
            index = load_index(Path(config.reports_dir))
            self.assertEqual(index["latest_success_run_id"], metadata.run_id)
            self.assertTrue(Path(metadata.report_path).exists())

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

    def test_runner_prevents_concurrent_runs(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            config.check_config = str(Path(td) / "check_config.json")
            Path(config.check_config).write_text("{}", encoding="utf-8")

            runner = ReportRunner(config, check_callable=lambda output, log: {})
            runner._active_run_id = "active"

            with self.assertRaises(RuntimeError) as ctx:
                runner.run_once("manual")

            self.assertIn("active", str(ctx.exception))
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
python -m unittest test_report_service.ReportServiceRunnerTest -v
```

Expected: FAIL because `image_check_service.runner` is missing.

- [ ] **Step 3: Implement runner**

Create `image_check_service/runner.py`:

```python
from __future__ import annotations

import contextlib
import datetime as dt
import io
import sys
import threading
import traceback
from pathlib import Path
from typing import Callable

import check_i18n_images

from .history import create_run_directory, record_failed_run, record_successful_run, write_metadata
from .models import RunMetadata, ServiceConfig


CheckCallable = Callable[[Path, Path], dict[str, int]]


def make_run_id(now: dt.datetime | None = None) -> str:
    return (now or dt.datetime.now()).strftime("%Y%m%d_%H%M%S")


def _now_text() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")


class ReportRunner:
    def __init__(self, config: ServiceConfig, check_callable: CheckCallable | None = None):
        self.config = config
        self.check_callable = check_callable or self._run_existing_checker
        self._lock = threading.Lock()
        self._active_run_id: str | None = None

    @property
    def active_run_id(self) -> str | None:
        return self._active_run_id

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
        write_metadata(run_dir, metadata)
        try:
            counts = self.check_callable(report_path, log_path)
            finished = dt.datetime.now()
            metadata.status = "success"
            metadata.finished_at = _now_text()
            metadata.duration_seconds = (finished - started).total_seconds()
            metadata.counts = counts
            write_metadata(run_dir, metadata)
            record_successful_run(reports_dir, metadata, self.config.history_success_limit)
            check_i18n_images.cleanup_ocr_cache_archive(
                Path(check_i18n_images.OCR_CACHE_DB_FILE),
                self.config.ocr_archive_retention_days,
            )
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
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = check_i18n_images.main(args)
        log_path.write_text(stderr.getvalue(), encoding="utf-8")
        if exit_code != 0:
            raise RuntimeError(f"check_i18n_images exited with {exit_code}")
        return {}
```

- [ ] **Step 4: Run runner tests**

Run:

```powershell
python -m unittest test_report_service.ReportServiceRunnerTest -v
```

Expected: PASS, 3 tests.

- [ ] **Step 5: Run service tests**

Run:

```powershell
python -m unittest test_report_service -v
```

Expected: PASS, all service tests so far.

- [ ] **Step 6: Commit**

```powershell
git add image_check_service/runner.py test_report_service.py
git commit -m "feat: add report runner orchestration"
```

## Task 5: Scheduler

**Files:**
- Create: `image_check_service/scheduler.py`
- Modify: `test_report_service.py`

- [ ] **Step 1: Add failing scheduler tests**

Append to `test_report_service.py`:

```python
from image_check_service.scheduler import next_daily_run


class ReportServiceSchedulerTest(unittest.TestCase):
    def test_next_daily_run_returns_today_when_time_is_future(self):
        now = dt.datetime(2026, 6, 10, 1, 30)

        result = next_daily_run("02:00", now)

        self.assertEqual(result, dt.datetime(2026, 6, 10, 2, 0))

    def test_next_daily_run_returns_tomorrow_when_time_has_passed(self):
        now = dt.datetime(2026, 6, 10, 3, 0)

        result = next_daily_run("02:00", now)

        self.assertEqual(result, dt.datetime(2026, 6, 11, 2, 0))
```

If `datetime as dt` is not already imported in this file, add:

```python
import datetime as dt
```

- [ ] **Step 2: Run scheduler tests to verify failure**

Run:

```powershell
python -m unittest test_report_service.ReportServiceSchedulerTest -v
```

Expected: FAIL because scheduler module is missing.

- [ ] **Step 3: Implement scheduler helper and loop**

Create `image_check_service/scheduler.py`:

```python
from __future__ import annotations

import datetime as dt
import threading
import time
from typing import Callable


def next_daily_run(daily_run_time: str, now: dt.datetime | None = None) -> dt.datetime:
    current = now or dt.datetime.now()
    hour, minute = [int(part) for part in daily_run_time.split(":")]
    candidate = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= current:
        candidate = candidate + dt.timedelta(days=1)
    return candidate


class DailyScheduler:
    def __init__(
        self,
        get_daily_run_time: Callable[[], str],
        run_scheduled: Callable[[], None],
        poll_seconds: float = 5.0,
    ):
        self.get_daily_run_time = get_daily_run_time
        self.run_scheduled = run_scheduled
        self.poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._next_run: dt.datetime | None = None

    @property
    def next_run(self) -> dt.datetime | None:
        return self._next_run

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True, name="report-service-scheduler")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._next_run = next_daily_run(self.get_daily_run_time())
            while not self._stop.is_set():
                if dt.datetime.now() >= self._next_run:
                    self.run_scheduled()
                    break
                time.sleep(self.poll_seconds)
```

- [ ] **Step 4: Run scheduler tests**

Run:

```powershell
python -m unittest test_report_service.ReportServiceSchedulerTest -v
```

Expected: PASS, 2 tests.

- [ ] **Step 5: Commit**

```powershell
git add image_check_service/scheduler.py test_report_service.py
git commit -m "feat: add daily report scheduler"
```

## Task 6: HTTP API and Console Page

**Files:**
- Create: `image_check_service/web.py`
- Modify: `test_report_service.py`

- [ ] **Step 1: Add failing web handler tests**

Append to `test_report_service.py`:

```python
from image_check_service.web import build_console_html, status_payload


class ReportServiceWebTest(unittest.TestCase):
    def test_status_payload_includes_latest_and_config_errors(self):
        with tempfile.TemporaryDirectory() as td:
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.reports_dir = str(Path(td) / "reports")
            payload = status_payload(config, active_run_id=None, next_run_text="2026-06-11 02:00:00", config_errors=["bad"])

            self.assertEqual(payload["status"], "idle")
            self.assertEqual(payload["next_scheduled_run"], "2026-06-11 02:00:00")
            self.assertEqual(payload["config_errors"], ["bad"])
            self.assertIn("latest_success_run_id", payload)

    def test_console_html_contains_required_controls(self):
        html = build_console_html()

        self.assertIn("I18n Image Check Service", html)
        self.assertIn("Run Now", html)
        self.assertIn("/api/status", html)
        self.assertIn("/api/runs", html)
        self.assertIn("daily_run_time", html)
```

- [ ] **Step 2: Run web tests to verify failure**

Run:

```powershell
python -m unittest test_report_service.ReportServiceWebTest -v
```

Expected: FAIL because web module is missing.

- [ ] **Step 3: Implement web module**

Create `image_check_service/web.py`:

```python
from __future__ import annotations

import json
import mimetypes
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

import check_i18n_images

from .config import save_config, validate_config
from .history import load_index
from .models import ServiceConfig
from .runner import ReportRunner


def status_payload(
    config: ServiceConfig,
    active_run_id: str | None,
    next_run_text: str | None,
    config_errors: list[str] | None = None,
) -> dict[str, object]:
    index = load_index(Path(config.reports_dir))
    return {
        "status": "running" if active_run_id else "idle",
        "active_run_id": active_run_id,
        "next_scheduled_run": next_run_text,
        "latest_success_run_id": index.get("latest_success_run_id"),
        "successful_runs": index.get("successful_runs", []),
        "failed_runs": index.get("failed_runs", []),
        "config": config.to_dict(),
        "config_errors": config_errors or validate_config(config),
    }


def build_console_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>I18n Image Check Service</title>
<style>
body { font-family: Arial, sans-serif; margin: 24px; background: #f6f7f9; color: #20242a; }
main { max-width: 1040px; margin: 0 auto; }
section { background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
button { padding: 8px 12px; cursor: pointer; }
button:disabled { opacity: .55; cursor: not-allowed; }
label { display: block; margin: 8px 0; }
input { padding: 6px; }
pre { white-space: pre-wrap; background: #f1f3f6; padding: 12px; }
</style>
</head>
<body>
<main>
<h1>I18n Image Check Service</h1>
<section>
  <h2>Status</h2>
  <p id="statusText">Loading...</p>
  <p id="nextRun"></p>
  <button id="runNow" onclick="runNow()">Run Now</button>
  <p><a id="currentReport" href="#" style="display:none">Open Current Report</a></p>
</section>
<section>
  <h2>Config</h2>
  <label>Daily run time <input id="daily_run_time" name="daily_run_time" value="02:00"></label>
  <label>Success history limit <input id="history_success_limit" name="history_success_limit" type="number" value="5"></label>
  <label>Failed history limit <input id="history_failed_limit" name="history_failed_limit" type="number" value="5"></label>
  <label>OCR archive retention days <input id="ocr_archive_retention_days" name="ocr_archive_retention_days" type="number" value="30"></label>
  <button onclick="saveConfig()">Save Config</button>
</section>
<section>
  <h2>Runs</h2>
  <pre id="runs"></pre>
</section>
</main>
<script>
async function refreshStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();
  document.getElementById('statusText').textContent = `Status: ${data.status}${data.active_run_id ? ' (' + data.active_run_id + ')' : ''}`;
  document.getElementById('nextRun').textContent = `Next scheduled run: ${data.next_scheduled_run || '-'}`;
  document.getElementById('runNow').disabled = data.status === 'running' || data.config_errors.length > 0;
  document.getElementById('daily_run_time').value = data.config.daily_run_time;
  document.getElementById('history_success_limit').value = data.config.history_success_limit;
  document.getElementById('history_failed_limit').value = data.config.history_failed_limit;
  document.getElementById('ocr_archive_retention_days').value = data.config.ocr_archive_retention_days;
  const link = document.getElementById('currentReport');
  if (data.latest_success_run_id) {
    link.href = `/reports/runs/${data.latest_success_run_id}/ui_image_check_report.html`;
    link.style.display = '';
  }
  document.getElementById('runs').textContent = JSON.stringify({successful: data.successful_runs, failed: data.failed_runs, errors: data.config_errors}, null, 2);
}
async function runNow() {
  await fetch('/api/runs', { method: 'POST' });
  refreshStatus();
}
async function saveConfig() {
  const body = {
    daily_run_time: document.getElementById('daily_run_time').value,
    history_success_limit: Number(document.getElementById('history_success_limit').value),
    history_failed_limit: Number(document.getElementById('history_failed_limit').value),
    ocr_archive_retention_days: Number(document.getElementById('ocr_archive_retention_days').value),
  };
  await fetch('/api/config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
  refreshStatus();
}
refreshStatus();
setInterval(refreshStatus, 3000);
</script>
</body>
</html>"""


class ReportServiceHandler(BaseHTTPRequestHandler):
    config: ServiceConfig
    config_path: Path
    runner: ReportRunner
    get_next_run_text: Callable[[], str | None]

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send_text(build_console_html(), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/status":
            self._send_json(status_payload(self.config, self.runner.active_run_id, self.get_next_run_text()))
            return
        if parsed.path == "/api/runs":
            index = load_index(Path(self.config.reports_dir))
            self._send_json(index)
            return
        if parsed.path.startswith("/reports/"):
            self._serve_report_file(parsed.path)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/runs":
            errors = validate_config(self.config)
            if errors:
                self._send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                metadata = self.runner.run_once("manual")
            except RuntimeError as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.CONFLICT)
                return
            self._send_json({"ok": True, "run": metadata.to_dict()}, status=HTTPStatus.ACCEPTED)
            return
        if parsed.path == "/api/config":
            self._handle_config_update()
            return
        if parsed.path == "/api/ocr-cache/operation":
            self._handle_ocr_operation()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_config_update(self) -> None:
        data = self._read_json()
        for key in ("daily_run_time", "history_success_limit", "history_failed_limit", "ocr_archive_retention_days"):
            if key in data:
                setattr(self.config, key, data[key])
        self.config.history_success_limit = int(self.config.history_success_limit)
        self.config.history_failed_limit = int(self.config.history_failed_limit)
        self.config.ocr_archive_retention_days = int(self.config.ocr_archive_retention_days)
        errors = validate_config(self.config)
        if errors:
            self._send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
            return
        save_config(self.config_path, self.config)
        self._send_json({"ok": True, "config": self.config.to_dict()})

    def _handle_ocr_operation(self) -> None:
        data = self._read_json()
        check_i18n_images.update_ocr_cache_operation_sqlite(
            Path(check_i18n_images.OCR_CACHE_DB_FILE),
            str(data["relativePath"]),
            str(data["md5"]),
            str(data["operation"]),
        )
        self._send_json({"ok": True})

    def _serve_report_file(self, url_path: str) -> None:
        relative = url_path.lstrip("/")
        target = (Path(self.config.reports_dir).parent / relative).resolve()
        reports_root = Path(self.config.reports_dir).resolve()
        if reports_root not in target.parents and target != reports_root:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        data = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        return data if isinstance(data, dict) else {}

    def _send_json(self, data: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_text(self, text: str, content_type: str) -> None:
        payload = text.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def create_server(
    config: ServiceConfig,
    config_path: Path,
    runner: ReportRunner,
    get_next_run_text: Callable[[], str | None],
) -> ThreadingHTTPServer:
    class BoundHandler(ReportServiceHandler):
        pass

    BoundHandler.config = config
    BoundHandler.config_path = config_path
    BoundHandler.runner = runner
    BoundHandler.get_next_run_text = get_next_run_text
    return ThreadingHTTPServer((config.host, config.port), BoundHandler)
```

- [ ] **Step 4: Run web tests**

Run:

```powershell
python -m unittest test_report_service.ReportServiceWebTest -v
```

Expected: PASS, 2 tests.

- [ ] **Step 5: Run all service tests**

Run:

```powershell
python -m unittest test_report_service -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add image_check_service/web.py test_report_service.py
git commit -m "feat: add report service web api"
```

## Task 7: Service Entrypoint

**Files:**
- Create: `report_service.py`
- Modify: `test_report_service.py`

- [ ] **Step 1: Add failing entrypoint tests**

Append to `test_report_service.py`:

```python
import report_service


class ReportServiceEntrypointTest(unittest.TestCase):
    def test_parse_args_accepts_config_path(self):
        args = report_service.parse_args(["--config", "custom.json"])

        self.assertEqual(args.config, "custom.json")

    def test_build_service_components_returns_runner_and_server(self):
        with tempfile.TemporaryDirectory() as td:
            config_path = Path(td) / "report_service_config.json"
            config = ServiceConfig(**DEFAULT_SERVICE_CONFIG)
            config.port = 0
            config.reports_dir = str(Path(td) / "reports")
            save_config(config_path, config)

            loaded, runner, scheduler, server = report_service.build_service_components(config_path)

            self.assertEqual(loaded.reports_dir, config.reports_dir)
            self.assertIsNotNone(runner)
            self.assertIsNotNone(scheduler)
            self.assertIsNotNone(server)
            server.server_close()
```

- [ ] **Step 2: Run entrypoint tests to verify failure**

Run:

```powershell
python -m unittest test_report_service.ReportServiceEntrypointTest -v
```

Expected: FAIL because `report_service.py` is missing.

- [ ] **Step 3: Implement entrypoint**

Create `report_service.py`:

```python
from __future__ import annotations

import argparse
import os
import webbrowser
from pathlib import Path

from image_check_service.config import load_or_create_config, validate_config
from image_check_service.runner import ReportRunner
from image_check_service.scheduler import DailyScheduler
from image_check_service.web import create_server


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the i18n image check management service.")
    parser.add_argument("--config", default="report_service_config.json", help="service config JSON path")
    parser.add_argument("--no-browser", action="store_true", help="do not open the console in a browser")
    return parser.parse_args(argv)


def build_service_components(config_path: Path):
    config = load_or_create_config(config_path)
    errors = validate_config(config)
    if errors:
        print("Service config has errors:")
        for error in errors:
            print(f"- {error}")
    runner = ReportRunner(config)
    scheduler = DailyScheduler(
        get_daily_run_time=lambda: config.daily_run_time,
        run_scheduled=lambda: runner.run_once("scheduled"),
    )
    server = create_server(
        config,
        config_path,
        runner,
        get_next_run_text=lambda: scheduler.next_run.strftime("%Y-%m-%d %H:%M:%S") if scheduler.next_run else None,
    )
    return config, runner, scheduler, server


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config)
    config, _runner, scheduler, server = build_service_components(config_path)
    scheduler.start()
    url = f"http://{config.host}:{server.server_address[1]}/"
    print(f"Report service started: {url}")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping report service...")
    finally:
        scheduler.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run entrypoint tests**

Run:

```powershell
python -m unittest test_report_service.ReportServiceEntrypointTest -v
```

Expected: PASS, 2 tests.

- [ ] **Step 5: Run all service tests**

Run:

```powershell
python -m unittest test_report_service -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add report_service.py test_report_service.py
git commit -m "feat: add report service entrypoint"
```

## Task 8: Integration Verification and Documentation

**Files:**
- Modify: `docs/superpowers/specs/2026-06-10-i18n-image-check-service-design.md`
- Optional create: `report_service_config.json` only if the team wants a checked-in default; otherwise rely on runtime creation.

- [ ] **Step 1: Run focused unit tests**

Run:

```powershell
python -m unittest test_report_service -v
```

Expected: PASS.

- [ ] **Step 2: Run existing image check tests**

Run:

```powershell
python -m unittest test_check_i18n_images -v
```

Expected: PASS or existing environment-dependent skips only.

- [ ] **Step 3: Start service on ephemeral port for smoke test**

Run:

```powershell
python report_service.py --config report_service_config.json --no-browser
```

Expected:

```text
Report service started: http://127.0.0.1:9080/
```

If port 9080 is occupied, temporarily edit generated `report_service_config.json` to `"port": 9081` and rerun. Stop with `Ctrl+C` after verifying startup.

- [ ] **Step 4: Smoke test status endpoint in a second terminal**

Run:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:9080/api/status | Select-Object -ExpandProperty Content
```

Expected: JSON containing `"status"`, `"latest_success_run_id"`, `"config"`, and `"config_errors"`.

- [ ] **Step 5: Update design doc implementation notes**

Append this section to `docs/superpowers/specs/2026-06-10-i18n-image-check-service-design.md`:

```markdown
## Implementation Notes

- The service entrypoint is `report_service.py`.
- Runtime service configuration is created at `report_service_config.json` when missing.
- Service-owned reports are stored under the configured `reports_dir`.
- The service cleanup only deletes directories under the configured service `reports/runs` root.
- OCR archive cleanup is implemented in `.ocr_cache.db` through `ocr_cache_archive`.
```

- [ ] **Step 6: Commit final documentation**

```powershell
git add docs/superpowers/specs/2026-06-10-i18n-image-check-service-design.md
git commit -m "docs: document report service implementation"
```

## Self-Review Checklist

- Spec coverage:
  - Persistent service: Tasks 6 and 7.
  - Manual page trigger: Tasks 6 and 7.
  - Daily scheduled run: Task 5 and Task 7.
  - Current report points to latest success: Task 2 and Task 4.
  - History retains 5 successful runs: Task 2.
  - Failed runs do not replace latest: Task 2 and Task 4.
  - Report asset cleanup: Task 2 retention deletes run dirs and assets.
  - OCR stale MD5 archive and retention: Task 3.
  - No source image deletion: Task 2 safe delete root and Task 8 verification.
- Placeholder scan:
  - No `TBD`, `TODO`, `implement later`, or vague unbounded placeholders are intentionally present.
- Type consistency:
  - `ServiceConfig`, `RunMetadata`, `ReportRunner`, `DailyScheduler`, `status_payload`, and `create_server` are used consistently across tasks.
