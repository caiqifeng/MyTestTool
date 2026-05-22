from pathlib import Path
from typing import Any

from yolo_game_verify.models import BoundingBox, Detection


class YOLO26Detector:
    def __init__(self, model: Any | None = None, model_path: str | None = None, model_name: str = "yolo26") -> None:
        if model is None:
            if model_path is None:
                raise ValueError("model_path is required when model is not provided")
            from ultralytics import YOLO

            model = YOLO(model_path)
        self.model = model
        self.name = model_name

    def detect(self, image_path: Path, frame_index: int) -> list[Detection]:
        results = self.model(str(image_path), verbose=False)
        detections: list[Detection] = []
        for result in results:
            names = getattr(result, "names", {})
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            classes = list(getattr(boxes, "cls", []))
            confidences = list(getattr(boxes, "conf", []))
            coordinates = list(getattr(boxes, "xyxy", []))
            for cls_id, confidence, xyxy in zip(classes, confidences, coordinates, strict=False):
                cls_index = int(cls_id)
                x1, y1, x2, y2 = [int(float(value)) for value in xyxy]
                detections.append(
                    Detection(
                        label=str(names.get(cls_index, cls_index)),
                        bbox=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                        confidence=float(confidence),
                        source=self.name,
                        frame_index=frame_index,
                    )
                )
        return detections
