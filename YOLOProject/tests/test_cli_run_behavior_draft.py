import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app
from yolo_game_verify.generation.models import BehaviorTreeDraft, GeneratedCaseDraft


def test_cli_run_behavior_draft_writes_events(tmp_path):
    draft_path = tmp_path / "draft.json"
    out = tmp_path / "behavior_run.json"
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
        behavior_tree=BehaviorTreeDraft(
            intent="verify reward",
            root={"type": "sequence", "children": [{"type": "action", "node_name": "ClaimReward"}]},
        ),
        assertion_config=[],
        generation_evidence=[],
        risk_level="low",
    )
    draft_path.write_text(draft.model_dump_json(), encoding="utf-8")

    result = CliRunner().invoke(app, ["run-behavior-draft", "--draft", str(draft_path), "--out", str(out)])

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["result"] == "pass"
    assert payload["events"][0]["name"] == "ClaimReward"
