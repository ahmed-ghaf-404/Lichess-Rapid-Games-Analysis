import json
import os

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)

def save_json(obj: dict, path: str):
    with open(path, "w") as f:
        json.dump(obj, f, indent=4, default=str)
