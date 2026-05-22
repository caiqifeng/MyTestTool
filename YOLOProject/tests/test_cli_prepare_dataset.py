import json

import cv2
import numpy as np
from typer.testing import CliRunner

from yolo_game_verify.cli import app


def test_cli_prepare_dataset_writes_manifest(tmp_path):
    frames = tmp_path / "frames"
    frames.mkdir()
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    cv2.imwrite(str(frames / "a.png"), image)
    cv2.imwrite(str(frames / "b.png"), image)
    out = tmp_path / "manifest.json"

    result = CliRunner().invoke(
        app,
        [
            "prepare-dataset",
            "--frames",
            str(frames),
            "--project",
            "pc_mmorpg",
            "--game-version",
            "1.2.3",
            "--environment",
            "blackbox",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["total_assets"] == 2
    assert payload["unique_assets"] == 1
