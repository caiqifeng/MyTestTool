from yolo_game_verify.models import (
    AssertionResult,
    BoundingBox,
    Detection,
    EvidenceFrame,
    VerificationReport,
)
from yolo_game_verify.detectors.base import Detector


def test_detection_serializes_with_bbox_and_source():
    detection = Detection(
        label="reward_popup",
        bbox=BoundingBox(x1=10, y1=20, x2=110, y2=80),
        confidence=0.91,
        source="yolo26",
        frame_index=2,
        text=None,
    )

    payload = detection.model_dump()

    assert payload["label"] == "reward_popup"
    assert payload["bbox"] == {"x1": 10, "y1": 20, "x2": 110, "y2": 80}
    assert payload["source"] == "yolo26"


def test_report_supports_unknown_result():
    report = VerificationReport(
        case_id="case_login_reward",
        result=AssertionResult.UNKNOWN,
        reason="reward evidence was not stable across enough frames",
        frames=[
            EvidenceFrame(
                frame_index=0,
                image_path="frame_000.png",
                detections=[],
            )
        ],
    )

    assert report.result == AssertionResult.UNKNOWN
    assert report.model_dump()["result"] == "unknown"


def test_detector_protocol_is_importable():
    assert Detector.__name__ == "Detector"
