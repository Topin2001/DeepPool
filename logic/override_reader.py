import json
import os

OVERRIDE_PATH = os.environ.get("OVERRIDE_PATH", "/config/override.json")

def read_override() -> bool | None:
    try:
        with open(OVERRIDE_PATH, 'r') as f:
            data = json.load(f)
            return data.get("state", None)
    except Exception as e:
        print(f"[WARN] Override load failed: {e} — no override applied")
        return None