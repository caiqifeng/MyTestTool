import json
from pathlib import Path

from yolo_game_verify.cases.models import StructuredCase


def load_structured_case(case_path: Path) -> StructuredCase:
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    return StructuredCase.model_validate(payload)
