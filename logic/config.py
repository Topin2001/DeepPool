import json
import os

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/config/config.json")

_DEFAULTS = {
    "temp_on": 28.0,
    "temp_off": 25.0,
    "gpio_pin_pump": 17,
    "gpio_pin_sw_on": 23,
    "gpio_pin_sw_off": 24,
    "loop_interval_seconds": 60
}

def load() -> dict:
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
            return {**_DEFAULTS, **cfg}  # les defaults comblent les clés manquantes
    except Exception as e:
        print(f"[WARN] Config load failed: {e} — using defaults")
        return _DEFAULTS.copy()