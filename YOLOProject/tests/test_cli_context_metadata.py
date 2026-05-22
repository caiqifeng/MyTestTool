import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app


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
