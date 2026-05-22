from pathlib import Path

import cv2
import numpy as np

from yolo_game_verify.detectors.yolo26 import YOLO26Detector


class FakeBoxes:
    cls = [0]
    conf = [0.88]
    xyxy = [[10, 20, 60, 80]]


class FakeResult:
    boxes = FakeBoxes()
    names = {0: "quest_complete_hint"}


class FakeModel:
    def __call__(self, image_path: str, verbose: bool = False):
        return [FakeResult()]


def test_yolo26_detector_maps_model_output(tmp_path: Path):
    frame = tmp_path / "frame.png"
    cv2.imwrite(str(frame), np.zeros((100, 100, 3), dtype=np.uint8))

    detector = YOLO26Detector(model=FakeModel(), model_name="fake-yolo26")
    detections = detector.detect(frame, frame_index=3)

    assert len(detections) == 1
    assert detections[0].label == "quest_complete_hint"
    assert detections[0].confidence == 0.88
    assert detections[0].bbox.x1 == 10
    assert detections[0].source == "fake-yolo26"
