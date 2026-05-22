import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app


def test_cli_evaluate_frames_writes_report(synthetic_frame_dir, tmp_path):
    runner = CliRunner()
    out = tmp_path / "report.json"

    result = runner.invoke(
        app,
        [
            "evaluate-frames",
            "--frames",
            str(synthetic_frame_dir),
            "--required-label",
            "reward_popup",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_id"] == "offline_frame_evaluation"
    assert payload["result"] in {"fail", "unknown", "pass"}
