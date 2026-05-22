import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app


def test_cli_generate_case_draft_writes_draft(tmp_path):
    case_path = tmp_path / "case.json"
    capability_path = tmp_path / "nodes.json"
    out = tmp_path / "draft.json"
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
                        "frame_dir": "frames/step_001",
                        "assertions": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    capability_path.write_text(
        json.dumps(
            [
                {
                    "node_name": "ClaimReward",
                    "module": "daily_task",
                    "input_parameters": {},
                    "preconditions": ["quest_complete_hint"],
                    "execution_action": "click claim reward",
                    "success_state": "reward_popup",
                    "failure_state": "error_popup",
                    "available_environments": ["blackbox"],
                    "risk_level": "low",
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
            "generate-case-draft",
            "--case",
            str(case_path),
            "--capabilities",
            str(capability_path),
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["draft_id"] == "draft_case_reward"
    assert payload["structured_case"]["steps"][0]["assertions"][0]["required_label"] == "reward_popup"
