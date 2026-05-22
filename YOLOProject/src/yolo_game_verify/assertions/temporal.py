from yolo_game_verify.models import AssertionResult, EvidenceFrame, TemporalAssertion


def evaluate_temporal_assertion(
    assertion: TemporalAssertion,
    frames: list[EvidenceFrame],
) -> tuple[AssertionResult, str]:
    matching_frames = 0
    for frame in frames:
        for detection in frame.detections:
            if detection.label == assertion.required_label and detection.confidence >= assertion.min_confidence:
                matching_frames += 1
                break

    if matching_frames >= assertion.min_frames:
        return AssertionResult.PASS, f"{assertion.required_label} appeared in {matching_frames} frames"

    if matching_frames > 0:
        return (
            AssertionResult.UNKNOWN,
            f"{assertion.required_label} appeared in {matching_frames} frame; required {assertion.min_frames}",
        )

    return AssertionResult.FAIL, f"{assertion.required_label} did not appear"
