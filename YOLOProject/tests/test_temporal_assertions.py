from yolo_game_verify.assertions.temporal import evaluate_temporal_assertion
from yolo_game_verify.models import (
    AssertionResult,
    BoundingBox,
    Detection,
    EvidenceFrame,
    TemporalAssertion,
)


def make_frame(index: int, label: str | None) -> EvidenceFrame:
    detections = []
    if label is not None:
        detections.append(
            Detection(
                label=label,
                bbox=BoundingBox(x1=1, y1=2, x2=3, y2=4),
                confidence=0.9,
                source="yolo26",
                frame_index=index,
            )
        )
    return EvidenceFrame(frame_index=index, image_path=f"frame_{index}.png", detections=detections)


def test_temporal_assertion_passes_when_label_appears_in_enough_frames():
    assertion = TemporalAssertion(assertion_id="reward_visible", required_label="reward_popup", min_frames=2)
    frames = [make_frame(0, "reward_popup"), make_frame(1, "reward_popup"), make_frame(2, None)]

    result, reason = evaluate_temporal_assertion(assertion, frames)

    assert result == AssertionResult.PASS
    assert reason == "reward_popup appeared in 2 frames"


def test_temporal_assertion_unknown_when_label_appears_once():
    assertion = TemporalAssertion(assertion_id="reward_visible", required_label="reward_popup", min_frames=2)
    frames = [make_frame(0, "reward_popup"), make_frame(1, None), make_frame(2, None)]

    result, reason = evaluate_temporal_assertion(assertion, frames)

    assert result == AssertionResult.UNKNOWN
    assert reason == "reward_popup appeared in 1 frame; required 2"


def test_temporal_assertion_fails_when_error_label_is_absent_after_all_frames():
    assertion = TemporalAssertion(assertion_id="error_visible", required_label="error_popup", min_frames=1)
    frames = [make_frame(0, None), make_frame(1, None)]

    result, reason = evaluate_temporal_assertion(assertion, frames)

    assert result == AssertionResult.FAIL
    assert reason == "error_popup did not appear"
