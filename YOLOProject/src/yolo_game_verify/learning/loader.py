import json
from pathlib import Path

from yolo_game_verify.cases.models import CaseVerificationReport


def load_case_reports(report_dir: Path) -> list[CaseVerificationReport]:
    report_paths = sorted(path for path in report_dir.iterdir() if path.suffix.lower() == ".json")
    reports: list[CaseVerificationReport] = []
    for report_path in report_paths:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        reports.append(CaseVerificationReport.model_validate(payload))
    return reports
