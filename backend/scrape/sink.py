import json
from pathlib import Path

class FileSystemSink:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    def save(self, username: str, game: dict):
        user_dir = self.base_path / username
        user_dir.mkdir(parents=True, exist_ok=True)

        path = user_dir / f"{game['id']}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(game, f, indent=2, default=str)
