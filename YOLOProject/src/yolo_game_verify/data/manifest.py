from pydantic import BaseModel, Field


class FrameAsset(BaseModel):
    path: str
    sha256: str
    width: int
    height: int
    duplicate_of: str | None = None


class DatasetManifest(BaseModel):
    project: str
    game_version: str
    environment: str
    total_assets: int
    unique_assets: int
    assets: list[FrameAsset] = Field(default_factory=list)


def build_manifest(
    assets: list[FrameAsset],
    project: str,
    game_version: str,
    environment: str,
) -> DatasetManifest:
    first_path_by_hash: dict[str, str] = {}
    resolved_assets: list[FrameAsset] = []
    for asset in assets:
        duplicate_of = first_path_by_hash.get(asset.sha256)
        if duplicate_of is None:
            first_path_by_hash[asset.sha256] = asset.path
        resolved_assets.append(asset.model_copy(update={"duplicate_of": duplicate_of}))

    return DatasetManifest(
        project=project,
        game_version=game_version,
        environment=environment,
        total_assets=len(resolved_assets),
        unique_assets=len(first_path_by_hash),
        assets=resolved_assets,
    )
