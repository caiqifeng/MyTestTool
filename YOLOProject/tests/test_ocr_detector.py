from pathlib import Path

import cv2
import numpy as np

from yolo_game_verify.detectors.ocr import OCRDetector


def fake_reader(image_path: Path) -> list[tuple[str, float]]:
    return [("任务完成", 0.93)]


def test_ocr_detector_emits_text_detection(tmp_path: Path):
    frame = tmp_path / "frame.png"
    cv2.imwrite(str(frame), np.zeros((80, 160, 3), dtype=np.uint8))

    detector = OCRDetector(reader=fake_reader)
    detections = detector.detect(frame, frame_index=1)

    assert detections[0].label == "ocr_text"
    assert detections[0].text == "任务完成"
    assert detections[0].confidence == 0.93
    assert detections[0].source == "ocr"
