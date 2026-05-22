import json

from yolo_game_verify.generation.models import BehaviorTreeDraft, GeneratedCaseDraft
from yolo_game_verify.generation.reporting import write_generated_case_draft
from yolo_game_verify.models import TemporalAssertion


def test_write_generated_case_draft(tmp_path):
    draft = GeneratedCaseDraft(
        draft_id="draft_case_reward",
        source_case_id="case_reward",
        structured_case={
            "case_id": "draft_case_reward",
            "case_name": "Generated reward verification",
            "project": "pc_mmorpg",
            "environment": "blackbox",
            "steps": [],
        },
        behavior_tree=BehaviorTreeDraft(intent="verify reward", root={"type": "sequence", "children": []}),
        assertion_config=[
            TemporalAssertion(
                assertion_id="reward_popup_visible",
                required_label="reward_popup",
                min_frames=2,
            )
        ],
        generation_evidence=["matched node ClaimReward from historical case"],
        risk_level="low",
    )
    out = tmp_path / "draft.json"

    write_generated_case_draft(draft, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["draft_id"] == "draft_case_reward"
    assert payload["review_state"] == "draft"
    assert payload["assertion_config"][0]["required_label"] == "reward_popup"
