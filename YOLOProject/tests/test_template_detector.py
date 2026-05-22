from pathlib import Path

import cv2
import numpy as np

from yolo_game_verify.detectors.template import TemplateDetector


def test_template_detector_finds_white_rectangle(tmp_path: Path):
    frame = tmp_path / "frame.png"
    template = tmp_path / "reward_template.png"

    image = np.zeros((120, 220, 3), dtype=np.uint8)
    cv2.rectangle(image, (40, 30), (100, 70), (255, 255, 255), -1)
    cv2.imwrite(str(frame), image)

    patch = image[30:70, 40:100]
    cv2.imwrite(str(template), patch)

    detector = TemplateDetector(label="reward_popup", template_path=template, threshold=0.95)
    detections = detector.detect(frame, frame_index=0)

    assert len(detections) == 1
    assert detections[0].label == "reward_popup"
    assert detections[0].confidence >= 0.95
    assert detections[0].bbox is not None
