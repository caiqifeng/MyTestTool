from pathlib import Path

from yolo_game_verify.detectors.adapter import DetectorAdapter
from yolo_game_verify.models import Detection, EvidenceFrame


class FakeDetector:
    name = "fake"

    def detect(self, image_path: Path, frame_index: int) -> list[Detection]:
        return [
            Detection(
                label="reward_popup",
                confidence=0.9,
                source=self.name,
                frame_index=frame_index,
            )
        ]


def test_detector_adapter_adds_detections_to_frame(tmp_path):
    frame_path = tmp_path / "frame.png"
    frame_path.write_bytes(b"fake")
    frame = EvidenceFrame.from_path(3, frame_path)

    enriched = DetectorAdapter([FakeDetector()]).enrich_frame(frame)

    assert enriched.detections[0].label == "reward_popup"
    assert enriched.detections[0].frame_index == 3
