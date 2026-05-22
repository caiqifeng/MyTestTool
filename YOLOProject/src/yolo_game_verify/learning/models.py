from pydantic import BaseModel, Field


class PatternSummary(BaseModel):
    key: str
    count: int
    case_ids: list[str] = Field(default_factory=list)


class NodeConfidence(BaseModel):
    node_name: str
    pass_rate: float
    observed_runs: int


class AssertionConfidence(BaseModel):
    assertion_id: str
    pass_rate: float
    observed_runs: int


class LearningSummary(BaseModel):
    total_reports: int
    result_counts: dict[str, int]
    failure_patterns: list[PatternSummary] = Field(default_factory=list)
    unknown_patterns: list[PatternSummary] = Field(default_factory=list)
    node_confidence: list[NodeConfidence] = Field(default_factory=list)
    assertion_confidence: list[AssertionConfidence] = Field(default_factory=list)
    coverage_gaps: list[str] = Field(default_factory=list)
    suggested_cases: list[str] = Field(default_factory=list)
