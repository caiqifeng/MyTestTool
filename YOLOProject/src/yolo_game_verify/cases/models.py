from pydantic import BaseModel, Field

from yolo_game_verify.models import AssertionResult, EvidenceFrame, TemporalAssertion


class StructuredStep(BaseModel):
    step_id: str
    name: str
    node_name: str
    frame_dir: str
    assertions: list[TemporalAssertion] = Field(default_factory=list)


class StructuredCase(BaseModel):
    case_id: str
    case_name: str
    project: str
    environment: str
    steps: list[StructuredStep]


class AssertionEvaluation(BaseModel):
    assertion_id: str
    result: AssertionResult
    reason: str


class StepVerificationResult(BaseModel):
    step_id: str
    result: AssertionResult
    reason: str
    assertion_results: list[AssertionEvaluation]
    frames: list[EvidenceFrame] = Field(default_factory=list)


class CaseVerificationReport(BaseModel):
    case_id: str
    case_name: str
    project: str
    environment: str
    result: AssertionResult
    reason: str
    steps: list[StepVerificationResult]
