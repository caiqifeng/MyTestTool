from typing import Any, Literal

from pydantic import BaseModel, Field

from yolo_game_verify.models import TemporalAssertion


class NodeCapability(BaseModel):
    node_name: str
    module: str
    input_parameters: dict[str, Any] = Field(default_factory=dict)
    preconditions: list[str] = Field(default_factory=list)
    execution_action: str
    success_state: str
    failure_state: str
    available_environments: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "medium"
    supported_assertions: list[TemporalAssertion] = Field(default_factory=list)


class BehaviorTreeDraft(BaseModel):
    intent: str
    root: dict[str, Any]


class GeneratedCaseDraft(BaseModel):
    draft_id: str
    source_case_id: str
    review_state: Literal["draft"] = "draft"
    structured_case: dict[str, Any]
    behavior_tree: BehaviorTreeDraft
    assertion_config: list[TemporalAssertion]
    generation_evidence: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "medium"
