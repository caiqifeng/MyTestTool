from yolo_game_verify.cases.models import StructuredCase, StructuredStep, StepVerificationResult
from yolo_game_verify.models import AssertionResult, TemporalAssertion


def test_structured_case_contains_steps_and_assertions():
    case = StructuredCase(
        case_id="case_daily_task_001",
        case_name="Daily task reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="complete daily task",
                node_name="CompleteDailyTask",
                frame_dir="frames/step_001",
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

    assert case.steps[0].assertions[0].required_label == "reward_popup"


def test_step_verification_result_serializes_result_state():
    result = StepVerificationResult(
        step_id="step_001",
        result=AssertionResult.UNKNOWN,
        reason="reward_popup appeared in 1 frame; required 2",
        assertion_results=[],
    )

    assert result.model_dump()["result"] == "unknown"
