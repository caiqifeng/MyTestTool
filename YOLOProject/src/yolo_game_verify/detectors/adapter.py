from yolo_game_verify.detectors.base import Detector
from yolo_game_verify.models import EvidenceFrame


class DetectorAdapter:
    def __init__(self, detectors: list[Detector]) -> None:
        self.detectors = detectors

    def enrich_frame(self, frame: EvidenceFrame) -> EvidenceFrame:
        detections = list(frame.detections)
        for detector in self.detectors:
            detections.extend(detector.detect(frame.image_path, frame.frame_index))
        return frame.model_copy(update={"detections": detections})
