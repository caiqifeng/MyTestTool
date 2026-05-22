from yolo_game_verify.cases.models import StructuredCase, StructuredStep
from yolo_game_verify.generation.generator import generate_case_draft
from yolo_game_verify.generation.models import NodeCapability
from yolo_game_verify.models import TemporalAssertion


def test_generate_case_draft_outputs_structured_case_behavior_tree_and_assertions():
    historical_case = StructuredCase(
        case_id="case_daily_task_001",
        case_name="Daily task reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="claim reward",
                node_name="ClaimReward",
                frame_dir="frames/step_001",
                assertions=[],
            )
        ],
    )
    capability = NodeCapability(
        node_name="ClaimReward",
        module="daily_task",
        input_parameters={"reward_type": "daily"},
        preconditions=["quest_complete_hint"],
        execution_action="click claim reward",
        success_state="reward_popup",
        failure_state="error_popup",
        available_environments=["blackbox"],
        risk_level="low",
        supported_assertions=[
            TemporalAssertion(
                assertion_id="reward_popup_visible",
                required_label="reward_popup",
                min_frames=2,
            )
        ],
    )

    draft = generate_case_draft(historical_case, [capability])

    assert draft.draft_id == "draft_case_daily_task_001"
    assert draft.review_state == "draft"
    assert draft.structured_case["steps"][0]["assertions"][0]["required_label"] == "reward_popup"
    assert draft.behavior_tree.root["children"][0]["node_name"] == "ClaimReward"
    assert draft.assertion_config[0].assertion_id == "reward_popup_visible"
    assert draft.risk_level == "low"


def test_generate_case_draft_keeps_existing_assertions_when_capability_is_missing():
    historical_case = StructuredCase(
        case_id="case_unknown_node",
        case_name="Unknown node verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="custom step",
                node_name="CustomNode",
                frame_dir="frames/step_001",
                assertions=[
                    TemporalAssertion(
                        assertion_id="custom_visible",
                        required_label="blocked_flow_hint",
                        min_frames=1,
                    )
                ],
            )
        ],
    )

    draft = generate_case_draft(historical_case, [])

    assert draft.structured_case["steps"][0]["assertions"][0]["required_label"] == "blocked_flow_hint"
    assert draft.risk_level == "medium"
    assert "no capability match for CustomNode" in draft.generation_evidence
