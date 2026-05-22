import json

from typer.testing import CliRunner

from yolo_game_verify.cases.models import CaseVerificationReport
from yolo_game_verify.cli import app
from yolo_game_verify.models import AssertionResult


def test_cli_evaluate_frames_includes_context_metadata(synthetic_frame_dir, tmp_path):
    context = tmp_path / "context.json"
    out = tmp_path / "report.json"
    context.write_text(
        json.dumps(
            {
                "project": "pc_mmorpg",
                "game_version": "1.2.3",
                "environment": "blackbox",
                "model_version": "yolo26-reward-v1",
                "dataset_version": "reward-dataset-2026-05",
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "evaluate-frames",
            "--frames",
            str(synthetic_frame_dir),
            "--out",
            str(out),
            "--context",
            str(context),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["metadata"]["context"]["model_version"] == "yolo26-reward-v1"


def test_cli_summarize_learning_includes_context_metadata(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    context = tmp_path / "context.json"
    capabilities = tmp_path / "capabilities.json"
    out = tmp_path / "learning.json"
    report = CaseVerificationReport(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        result=AssertionResult.PASS,
        reason="ok",
        steps=[],
    )
    (reports / "case_reward.json").write_text(report.model_dump_json(), encoding="utf-8")
    capabilities.write_text(
        json.dumps(
            [
                {
                    "node_name": "ClaimReward",
                    "module": "daily_task",
                    "execution_action": "claim reward",
                    "success_state": "reward_popup",
                    "failure_state": "error_popup",
                    "supported_assertions": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    context.write_text(json.dumps({"game_version": "1.2.3", "dataset_version": "dataset-v1"}), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "summarize-learning",
            "--reports",
            str(reports),
            "--capabilities",
            str(capabilities),
            "--out",
            str(out),
            "--context",
            str(context),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["metadata"]["context"]["dataset_version"] == "dataset-v1"
