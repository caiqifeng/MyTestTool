from pathlib import Path

from yolo_game_verify.generation.models import GeneratedCaseDraft


def write_generated_case_draft(draft: GeneratedCaseDraft, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(draft.model_dump_json(indent=2), encoding="utf-8")
