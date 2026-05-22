from collections.abc import Callable
from pathlib import Path

from yolo_game_verify.models import Detection

OCRReader = Callable[[Path], list[tuple[str, float]]]


class OCRDetector:
    name = "ocr"

    def __init__(self, reader: OCRReader) -> None:
        self.reader = reader

    def detect(self, image_path: Path, frame_index: int) -> list[Detection]:
        detections: list[Detection] = []
        for text, confidence in self.reader(image_path):
            detections.append(
                Detection(
                    label="ocr_text",
                    bbox=None,
                    confidence=float(confidence),
                    source=self.name,
                    frame_index=frame_index,
                    text=text,
                )
            )
        return detections
