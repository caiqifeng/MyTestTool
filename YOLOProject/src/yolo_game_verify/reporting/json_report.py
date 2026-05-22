from pathlib import Path

from yolo_game_verify.models import VerificationReport


def write_json_report(report: VerificationReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
