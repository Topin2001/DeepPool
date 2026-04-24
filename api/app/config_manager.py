import json
import os

CONFIG_PATH   = os.environ.get("CONFIG_PATH",   "/config/config.json")
SCHEDULE_PATH = os.environ.get("SCHEDULE_PATH", "/config/schedule.json")
OVERRIDE_PATH = os.environ.get("OVERRIDE_PATH", "/config/override.json")

# --- Config ---

def read_config() -> dict:
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def write_config(data: dict):
    current = read_config()
    current.update(data)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(current, f, indent=4)

# --- Schedule ---

def read_schedule() -> dict:
    with open(SCHEDULE_PATH, 'r') as f:
        return json.load(f)

def write_schedule(data: dict):
    with open(SCHEDULE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# --- Override ---

def read_override() -> dict:
    with open(OVERRIDE_PATH, 'r') as f:
        return json.load(f)

def write_override(state):
    with open(OVERRIDE_PATH, 'w') as f:
        json.dump({"state": state}, f, indent=4)