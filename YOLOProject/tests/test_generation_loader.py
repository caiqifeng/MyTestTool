import json

from yolo_game_verify.generation.loader import load_node_capabilities


def test_load_node_capabilities_from_json(tmp_path):
    capability_path = tmp_path / "nodes.json"
    capability_path.write_text(
        json.dumps(
            [
                {
                    "node_name": "ClaimReward",
                    "module": "daily_task",
                    "input_parameters": {"reward_type": "daily"},
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

    capabilities = load_node_capabilities(capability_path)

    assert capabilities[0].node_name == "ClaimReward"
    assert capabilities[0].supported_assertions[0].required_label == "reward_popup"
