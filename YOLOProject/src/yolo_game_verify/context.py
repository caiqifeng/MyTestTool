import json
from pathlib import Path

from pydantic import BaseModel


class VerificationContext(BaseModel):
    project: str | None = None
    game_version: str | None = None
    environment: str | None = None
    model_version: str | None = None
    dataset_version: str | None = None
    execution_id: str | None = None


def load_verification_context(context_path: Path) -> VerificationContext:
    payload = json.loads(context_path.read_text(encoding="utf-8"))
    return VerificationContext.model_validate(payload)
