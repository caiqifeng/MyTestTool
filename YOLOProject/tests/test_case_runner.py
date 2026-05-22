from yolo_game_verify.cases.models import StructuredCase, StructuredStep
from yolo_game_verify.cases.runner import evaluate_structured_case
from yolo_game_verify.models import AssertionResult, BoundingBox, Detection, TemporalAssertion


def test_evaluate_structured_case_passes_when_step_assertion_passes(synthetic_frame_dir):
    case = StructuredCase(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="claim reward",
                node_name="ClaimReward",
                frame_dir=str(synthetic_frame_dir),
                assertions=[
                    TemporalAssertion(
                        assertion_id="reward_popup_visible",
                        required_label="reward_popup",
                        min_frames=2,
                    )
                ],
            )
        ],
    )

    def detector(frame):
        frame.detections.append(
            Detection(
                label="reward_popup",
                bbox=BoundingBox(x1=1, y1=1, x2=20, y2=20),
                confidence=0.9,
                source="fake",
                frame_index=frame.frame_index,
            )
        )
        return frame

    report = evaluate_structured_case(case, frame_enricher=detector)

    assert report.result == AssertionResult.PASS
    assert report.steps[0].assertion_results[0].result == AssertionResult.PASS


def test_evaluate_structured_case_unknown_when_evidence_is_partial(synthetic_frame_dir):
    case = StructuredCase(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="claim reward",
                node_name="ClaimReward",
                frame_dir=str(synthetic_frame_dir),
                assertions=[
                    TemporalAssertion(
                        assertion_id="reward_popup_visible",
                        required_label="reward_popup",
                        min_frames=2,
                    )
                ],
            )
        ],
    )

    def detector(frame):
        if frame.frame_index == 0:
            frame.detections.append(
                Detection(
                    label="reward_popup",
                    bbox=BoundingBox(x1=1, y1=1, x2=20, y2=20),
                    confidence=0.9,
                    source="fake",
                    frame_index=frame.frame_index,
                )
            )
        return frame

    report = evaluate_structured_case(case, frame_enricher=detector)

    assert report.result == AssertionResult.UNKNOWN
    assert "required 2" in report.reason
