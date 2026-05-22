from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AssertionResult(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)


class Detection(BaseModel):
    label: str
    bbox: BoundingBox | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    source: str
    frame_index: int
    text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceFrame(BaseModel):
    frame_index: int
    image_path: str
    detections: list[Detection] = Field(default_factory=list)

    @classmethod
    def from_path(cls, frame_index: int, image_path: Path) -> "EvidenceFrame":
        return cls(frame_index=frame_index, image_path=str(image_path), detections=[])


class TemporalAssertion(BaseModel):
    assertion_id: str
    required_label: str
    expected: str = Field(default="present", pattern="^(present|absent)$")
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    min_frames: int = Field(default=2, ge=1)


class VerificationReport(BaseModel):
    case_id: str
    result: AssertionResult
    reason: str
    frames: list[EvidenceFrame]
    metadata: dict[str, Any] = Field(default_factory=dict)
