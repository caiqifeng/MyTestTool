import json

from typer.testing import CliRunner

from yolo_game_verify.cases.models import (
    AssertionEvaluation,
    CaseVerificationReport,
    StepVerificationResult,
)
from yolo_game_verify.cli import app
from yolo_game_verify.models import AssertionResult


def test_cli_summarize_learning_writes_summary(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    capability_path = tmp_path / "capabilities.json"
    out = tmp_path / "learning.json"
    report = CaseVerificationReport(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        result=AssertionResult.FAIL,
        reason="reward_popup did not appear",
        steps=[
            StepVerificationResult(
                step_id="step_001",
                result=AssertionResult.FAIL,
                reason="reward_popup did not appear",
                assertion_results=[
                    AssertionEvaluation(
                        assertion_id="reward_popup_visible",
                        result=AssertionResult.FAIL,
                        reason="reward_popup did not appear",
                    )
                ],
                frames=[],
            )
        ],
    )
    (reports / "case_reward.json").write_text(report.model_dump_json(), encoding="utf-8")
    capability_path.write_text(
        json.dumps(
            [
                {
                    "node_name": "ClaimReward",
                    "module": "daily_task",
                    "execution_action": "claim reward",
                    "success_state": "reward_popup",
                    "failure_state": "error_popup",
                    "supported_assertions": [
                        {
                            "assertion_id": "reward_popup_visible",
                            "required_label": "reward_popup",
                            "min_confidence": 0.5,
                            "min_frames": 2,
                        }
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "summarize-learning",
            "--reports",
            str(reports),
            "--capabilities",
            str(capability_path),
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["total_reports"] == 1
    assert payload["failure_patterns"][0]["key"] == "reward_popup did not appear"
