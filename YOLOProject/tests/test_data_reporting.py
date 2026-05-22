import json

from yolo_game_verify.data.manifest import DatasetManifest
from yolo_game_verify.data.reporting import write_dataset_manifest


def test_write_dataset_manifest(tmp_path):
    manifest = DatasetManifest(
        project="pc_mmorpg",
        game_version="1.2.3",
        environment="blackbox",
        total_assets=0,
        unique_assets=0,
        assets=[],
    )
    out = tmp_path / "manifest.json"

    write_dataset_manifest(manifest, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["project"] == "pc_mmorpg"
