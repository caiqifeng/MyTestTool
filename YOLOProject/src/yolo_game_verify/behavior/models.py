from pydantic import BaseModel, Field

from yolo_game_verify.models import AssertionResult


class BehaviorEvent(BaseModel):
    node_type: str
    name: str
    result: AssertionResult


class BehaviorRunResult(BaseModel):
    result: AssertionResult
    events: list[BehaviorEvent] = Field(default_factory=list)
