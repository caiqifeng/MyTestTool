from pathlib import Path

from yolo_game_verify.models import EvidenceFrame


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}


def load_step_frames(frame_dir: Path) -> list[EvidenceFrame]:
    image_paths = sorted(path for path in frame_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
    return [EvidenceFrame.from_path(index, path) for index, path in enumerate(image_paths)]
