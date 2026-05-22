from pathlib import Path

from yolo_game_verify.learning.models import LearningSummary


def write_learning_summary(summary: LearningSummary, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
