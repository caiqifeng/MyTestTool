from yolo_game_verify.models import AssertionResult

from pydantic import BaseModel


class ReviewDecision(BaseModel):
    reviewer: str
    approved: bool
    notes: str = ""


class TrialRunResult(BaseModel):
    run_id: str
    result: AssertionResult
    report_path: str
