from pathlib import Path

from yolo_game_verify.behavior.models import BehaviorRunResult


def write_behavior_run_result(result: BehaviorRunResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
