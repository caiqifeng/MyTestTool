from yolo_game_verify.generation.models import (
    BehaviorTreeDraft,
    GeneratedCaseDraft,
    NodeCapability,
)
from yolo_game_verify.models import TemporalAssertion


def test_node_capability_serializes_supported_assertions():
    capability = NodeCapability(
        node_name="ClaimReward",
        module="daily_task",
        input_parameters={"reward_type": "daily"},
        preconditions=["main_ui_visible"],
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

    payload = capability.model_dump()

    assert payload["node_name"] == "ClaimReward"
    assert payload["supported_assertions"][0]["required_label"] == "reward_popup"


def test_generated_case_draft_contains_three_outputs():
    assertion = TemporalAssertion(
        assertion_id="reward_popup_visible",
        required_label="reward_popup",
        min_frames=2,
    )
    draft = GeneratedCaseDraft(
        draft_id="draft_case_daily_task_001",
        source_case_id="case_daily_task_001",
        review_state="draft",
        structured_case={
            "case_id": "draft_case_daily_task_001",
            "case_name": "Generated daily task reward verification",
            "project": "pc_mmorpg",
            "environment": "blackbox",
            "steps": [],
        },
        behavior_tree=BehaviorTreeDraft(
            intent="verify reward popup",
            root={"type": "sequence", "children": []},
        ),
        assertion_config=[assertion],
        generation_evidence=["matched node ClaimReward from historical case"],
        risk_level="low",
    )

    payload = draft.model_dump()

    assert payload["review_state"] == "draft"
    assert payload["structured_case"]["case_id"] == "draft_case_daily_task_001"
    assert payload["behavior_tree"]["intent"] == "verify reward popup"
    assert payload["assertion_config"][0]["required_label"] == "reward_popup"
