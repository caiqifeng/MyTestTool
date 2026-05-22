import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app
from yolo_game_verify.generation.models import BehaviorTreeDraft, GeneratedCaseDraft


def write_draft(path):
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
        assertion_config=[],
        generation_evidence=[],
        risk_level="low",
    )
    path.write_text(draft.model_dump_json(), encoding="utf-8")


def test_cli_review_trial_and_promote_draft(tmp_path):
    draft_path = tmp_path / "draft.json"
    reviewed = tmp_path / "reviewed.json"
    trialed = tmp_path / "trialed.json"
    official = tmp_path / "official.json"
    write_draft(draft_path)

    review_result = CliRunner().invoke(
        app,
        [
            "review-draft",
            "--draft",
            str(draft_path),
            "--reviewer",
            "qa_lead",
            "--approved",
            "--out",
            str(reviewed),
        ],
    )
    trial_result = CliRunner().invoke(
        app,
        [
            "trial-draft",
            "--draft",
            str(reviewed),
            "--run-id",
            "trial_001",
            "--result",
            "pass",
            "--report-path",
            "reports/trial.json",
            "--out",
            str(trialed),
        ],
    )
    promote_result = CliRunner().invoke(app, ["promote-draft", "--draft", str(trialed), "--out", str(official)])

    assert review_result.exit_code == 0
    assert trial_result.exit_code == 0
    assert promote_result.exit_code == 0
    payload = json.loads(official.read_text(encoding="utf-8"))
    assert payload["review_state"] == "official"
