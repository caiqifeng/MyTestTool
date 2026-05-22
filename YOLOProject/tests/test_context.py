import json

from yolo_game_verify.context import VerificationContext, load_verification_context


def test_verification_context_serializes_versions():
    context = VerificationContext(
        project="pc_mmorpg",
        game_version="1.2.3",
        environment="blackbox",
        model_version="yolo26-reward-v1",
        dataset_version="reward-dataset-2026-05",
        execution_id="run_001",
    )

    payload = context.model_dump()

    assert payload["game_version"] == "1.2.3"
    assert payload["model_version"] == "yolo26-reward-v1"


def test_load_verification_context_from_json(tmp_path):
    context_path = tmp_path / "context.json"
    context_path.write_text(
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

    context = load_verification_context(context_path)

    assert context.dataset_version == "reward-dataset-2026-05"
