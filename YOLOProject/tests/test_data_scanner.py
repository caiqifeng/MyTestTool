from pathlib import Path

import cv2
import numpy as np

from yolo_game_verify.data.scanner import scan_frame_assets


def test_scan_frame_assets_reads_dimensions_and_hashes(tmp_path: Path):
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    frame = tmp_path / "frame.png"
    ignored = tmp_path / "notes.txt"
    cv2.imwrite(str(frame), image)
    ignored.write_text("ignore", encoding="utf-8")

    assets = scan_frame_assets(tmp_path)

    assert len(assets) == 1
    assert assets[0].path.endswith("frame.png")
    assert assets[0].width == 120
    assert assets[0].height == 80
    assert len(assets[0].sha256) == 64
