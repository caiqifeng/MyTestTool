from pathlib import Path

import cv2
import numpy as np
import pytest


@pytest.fixture()
def synthetic_frame_dir(tmp_path: Path) -> Path:
    frames = tmp_path / "frames"
    frames.mkdir()
    for idx in range(3):
        image = np.zeros((120, 220, 3), dtype=np.uint8)
        cv2.rectangle(image, (20 + idx * 10, 30), (100 + idx * 10, 80), (255, 255, 255), -1)
        cv2.imwrite(str(frames / f"frame_{idx:03d}.png"), image)
    return frames
