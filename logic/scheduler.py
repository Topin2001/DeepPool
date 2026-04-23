import json
import os
from datetime import datetime, time

SCHEDULE_PATH = os.environ.get("SCHEDULE_PATH", "/config/schedule.json")

_DEFAULTS = {
    "enabled": True,
    "slots": []
}

def _load() -> dict:
    try:
        with open(SCHEDULE_PATH, 'r') as f:
            cfg = json.load(f)
            return {**_DEFAULTS, **cfg}
    except Exception as e:
        print(f"[WARN] Schedule load failed: {e} — schedule disabled")
        return _DEFAULTS.copy()

def _parse_time(t_str: str) -> time:
    h, m = t_str.split(":")
    return time(int(h), int(m))

def _slot_is_active(slot: dict, now: time, temp: float) -> bool:
    start = _parse_time(slot["start"])
    end   = _parse_time(slot["end"])

    # Extensions température (pour le futur, ignorées si liste vide)
    extra_before = 0
    extra_after  = 0
    for ext in slot.get("temp_extensions", []):
        if temp >= ext["above"]:
            extra_before = max(extra_before, ext.get("extend_minutes", 0))
            extra_after  = max(extra_after,  ext.get("extend_minutes", 0))

    # Appliquer les extensions
    start_dt = datetime.combine(datetime.today(), start)
    end_dt   = datetime.combine(datetime.today(), end)
    from datetime import timedelta
    start_dt -= timedelta(minutes=extra_before)
    end_dt   += timedelta(minutes=extra_after)

    now_dt = datetime.combine(datetime.today(), now)
    return start_dt <= now_dt <= end_dt

def schedule_wants_pump(temp: float) -> bool | None:
    schedule = _load()

    if not schedule["enabled"]:
        return None

    now = datetime.now().time()
    for slot in schedule["slots"]:
        if _slot_is_active(slot, now, temp):
            return True

    return None  # pas dans une plage → on ne force rien