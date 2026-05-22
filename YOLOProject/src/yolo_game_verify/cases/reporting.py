from pathlib import Path

from yolo_game_verify.cases.models import CaseVerificationReport


def write_case_report(report: CaseVerificationReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
