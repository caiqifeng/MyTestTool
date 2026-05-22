from yolo_game_verify.data.manifest import FrameAsset, build_manifest


def test_build_manifest_marks_duplicate_hashes():
    assets = [
        FrameAsset(path="a.png", sha256="same", width=100, height=80),
        FrameAsset(path="b.png", sha256="same", width=100, height=80),
        FrameAsset(path="c.png", sha256="different", width=120, height=90),
    ]

    manifest = build_manifest(
        assets,
        project="pc_mmorpg",
        game_version="1.2.3",
        environment="blackbox",
    )

    assert manifest.project == "pc_mmorpg"
    assert manifest.total_assets == 3
    assert manifest.unique_assets == 2
    assert manifest.assets[1].duplicate_of == "a.png"
