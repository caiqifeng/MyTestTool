from pathlib import Path
from typing import Protocol

from yolo_game_verify.models import Detection


class Detector(Protocol):
    name: str

    def detect(self, image_path: Path, frame_index: int) -> list[Detection]:
        """Return detections for one image frame."""
        ...
