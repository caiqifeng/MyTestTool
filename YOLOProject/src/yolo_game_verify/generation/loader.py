import json
from pathlib import Path

from yolo_game_verify.generation.models import NodeCapability


def load_node_capabilities(capability_path: Path) -> list[NodeCapability]:
    payload = json.loads(capability_path.read_text(encoding="utf-8"))
    return [NodeCapability.model_validate(item) for item in payload]
