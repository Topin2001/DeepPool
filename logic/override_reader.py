import json
import os

OVERRIDE_PATH = os.environ.get("OVERRIDE_PATH", "/config/override.json")

def read_override() -> dict:
    try:
        with open(OVERRIDE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Override load failed: {e} — no override applied")
        return {"web": None, "physical": None}