import json
from pathlib import Path


class LocalArtifactStorage:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_json(self, key: str, payload: dict) -> str:
        path = self.root / f"{key}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)
