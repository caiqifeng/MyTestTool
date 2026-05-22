from pathlib import Path

from yolo_game_verify.data.manifest import DatasetManifest


def write_dataset_manifest(manifest: DatasetManifest, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
