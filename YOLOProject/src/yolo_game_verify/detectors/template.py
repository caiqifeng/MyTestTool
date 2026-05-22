from pathlib import Path

import cv2

from yolo_game_verify.models import BoundingBox, Detection


class TemplateDetector:
    name = "template"

    def __init__(self, label: str, template_path: Path, threshold: float = 0.9) -> None:
        self.label = label
        self.template_path = template_path
        self.threshold = threshold
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"template image not readable: {template_path}")
        self.template = template

    def detect(self, image_path: Path, frame_index: int) -> list[Detection]:
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"frame image not readable: {image_path}")

        result = cv2.matchTemplate(image, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < self.threshold:
            return []

        height, width = self.template.shape[:2]
        x1, y1 = max_loc
        bbox = BoundingBox(x1=x1, y1=y1, x2=x1 + width, y2=y1 + height)
        return [
            Detection(
                label=self.label,
                bbox=bbox,
                confidence=float(max_val),
                source=self.name,
                frame_index=frame_index,
            )
        ]
