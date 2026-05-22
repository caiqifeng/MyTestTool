import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app


def test_cli_evaluate_case_writes_report(synthetic_frame_dir, tmp_path):
    case_path = tmp_path / "case.json"
    out = tmp_path / "case_report.json"
    case_path.write_text(
        json.dumps(
            {
                "case_id": "case_reward",
                "case_name": "Reward verification",
                "project": "pc_mmorpg",
                "environment": "blackbox",
                "steps": [
                    {
                        "step_id": "step_001",
                        "name": "claim reward",
                        "node_name": "ClaimReward",
                        "frame_dir": str(synthetic_frame_dir),
                        "assertions": [
                            {
                                "assertion_id": "reward_popup_visible",
                                "required_label": "reward_popup",
                                "min_confidence": 0.5,
                                "min_frames": 2,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["evaluate-case", "--case", str(case_path), "--out", str(out)])

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_id"] == "case_reward"
    assert payload["steps"][0]["step_id"] == "step_001"
