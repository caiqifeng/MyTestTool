from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from .models import RunMetadata


INDEX_NAME = "index.json"


def _default_index() -> dict[str, Any]:
    return {
        "latest_success_run_id": None,
        "successful_runs": [],
        "failed_runs": [],
    }


def load_index(reports_dir: Path) -> dict[str, Any]:
    path = reports_dir / INDEX_NAME
    if not path.exists():
        return _default_index()

    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        return _default_index()

    index = _default_index()
    index.update(data)
    index["successful_runs"] = list(index.get("successful_runs") or [])
    index["failed_runs"] = list(index.get("failed_runs") or [])
    return index


def save_index(reports_dir: Path, index: dict[str, Any]) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(index, ensure_ascii=False, indent=2, default=str)
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(reports_dir)) as tmp:
        tmp.write(payload)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, reports_dir / INDEX_NAME)


def create_run_directory(reports_dir: Path, run_id: str) -> Path:
    run_dir = reports_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_metadata(run_dir: Path, metadata: RunMetadata) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2, default=str)
    (run_dir / "metadata.json").write_text(payload + "\n", encoding="utf-8")


def read_metadata(run_dir: Path) -> RunMetadata:
    data = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("run metadata must be a JSON object")
    return RunMetadata.from_dict(data)


def _delete_service_run_dir(reports_dir: Path, run_id: str) -> None:
    reports_root = reports_dir.resolve()
    runs_path = reports_dir / "runs"
    if runs_path.is_symlink():
        raise ValueError(f"refusing to delete from symlinked service run root: {runs_path}")

    runs_root = runs_path.resolve()
    if runs_root == reports_root or reports_root not in runs_root.parents:
        raise ValueError(f"refusing to delete from service run root outside reports dir: {runs_root}")

    target = (runs_path / run_id).resolve()
    if target == runs_root or runs_root not in target.parents:
        raise ValueError(f"refusing to delete outside service run root: {target}")
    if target.exists():
        shutil.rmtree(target)


def _trim_runs(reports_dir: Path, runs: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
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
    runs = [
        item
        for item in index["successful_runs"]
        if isinstance(item, dict) and item.get("run_id") != metadata.run_id
    ]
    runs.append(metadata.to_dict())
    index["latest_success_run_id"] = metadata.run_id
    index["successful_runs"] = _trim_runs(reports_dir, runs, success_limit)
    save_index(reports_dir, index)


def record_failed_run(reports_dir: Path, metadata: RunMetadata, failed_limit: int) -> None:
    index = load_index(reports_dir)
    runs = [
        item
        for item in index["failed_runs"]
        if isinstance(item, dict) and item.get("run_id") != metadata.run_id
    ]
    runs.append(metadata.to_dict())
    index["failed_runs"] = _trim_runs(reports_dir, runs, failed_limit)
    save_index(reports_dir, index)
