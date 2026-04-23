import json
import os
from datetime import datetime, time, timedelta

SCHEDULE_PATH = os.environ.get("SCHEDULE_PATH", "/config/schedule.json")

def _load() -> list:
    try:
        with open(SCHEDULE_PATH, 'r') as f:
            data = json.load(f)
            return data.get("schedule", [])
    except Exception as e:
        print(f"[WARN] Schedule load failed: {e} — schedule disabled")
        return []

def _parse_time(t_str: str) -> time:
    h, m = t_str.split(":")
    return time(int(h), int(m))

def _slot_is_active(slot: dict, now: datetime, temp: float) -> bool:
    start_dt = datetime.combine(now.date(), _parse_time(slot["start"]))
    end_dt   = datetime.combine(now.date(), _parse_time(slot["end"]))

    for ext in slot.get("temp_extensions", []):
        if temp >= ext["above"]:
            start_dt -= timedelta(minutes=ext["extend_minutes"])
            end_dt   += timedelta(minutes=ext["extend_minutes"])

    return start_dt <= now <= end_dt

def schedule_wants_pump(temp: float) -> bool | None:
    slots = _load()

    if not slots:
        return None  # fichier absent ou vide → température décide

    now = datetime.now()
    for slot in slots:
        if _slot_is_active(slot, now, temp):
            return True

    return None  # hors plage → température décide