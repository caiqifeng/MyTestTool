import json

from yolo_game_verify.cases.loader import load_structured_case


def test_load_structured_case_from_json(tmp_path):
    case_path = tmp_path / "case.json"
    case_path.write_text(
        json.dumps(
            {
                "case_id": "case_daily_task_001",
                "case_name": "Daily task reward verification",
                "project": "pc_mmorpg",
                "environment": "blackbox",
                "steps": [
                    {
                        "step_id": "step_001",
                        "name": "complete daily task",
                        "node_name": "CompleteDailyTask",
                        "frame_dir": "frames/step_001",
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

    case = load_structured_case(case_path)

    assert case.case_id == "case_daily_task_001"
    assert case.steps[0].assertions[0].required_label == "reward_popup"
