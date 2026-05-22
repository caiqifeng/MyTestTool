import hashlib
from pathlib import Path

from PIL import Image

from yolo_game_verify.data.manifest import FrameAsset

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_frame_assets(frame_dir: Path) -> list[FrameAsset]:
    assets: list[FrameAsset] = []
    image_paths = sorted(path for path in frame_dir.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES)
    for image_path in image_paths:
        with Image.open(image_path) as image:
            width, height = image.size
        assets.append(
            FrameAsset(
                path=str(image_path),
                sha256=_sha256(image_path),
                width=width,
                height=height,
            )
        )
    return assets
