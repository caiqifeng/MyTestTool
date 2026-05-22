import json

import cv2
import numpy as np
from typer.testing import CliRunner

from yolo_game_verify.cli import app


def test_cli_evaluate_frames_uses_template_detector(tmp_path):
    frames = tmp_path / "frames"
    frames.mkdir()
    frame = frames / "frame_000.png"
    template = tmp_path / "template.png"
    image = np.zeros((120, 220, 3), dtype=np.uint8)
    cv2.rectangle(image, (40, 30), (100, 70), (255, 255, 255), -1)
    cv2.imwrite(str(frame), image)
    cv2.imwrite(str(template), image[30:70, 40:100])
    out = tmp_path / "report.json"

    result = CliRunner().invoke(
        app,
        [
            "evaluate-frames",
            "--frames",
            str(frames),
            "--required-label",
            "reward_popup",
            "--min-frames",
            "1",
            "--template",
            str(template),
            "--template-label",
            "reward_popup",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["result"] == "pass"
    assert payload["frames"][0]["detections"][0]["label"] == "reward_popup"
