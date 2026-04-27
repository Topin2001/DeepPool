import json
import os
from datetime import datetime, time, timedelta
import influx_reader

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

def _compute_end(slot: dict, avg_temp: float) -> datetime:
    end_dt = datetime.combine(datetime.today(), _parse_time(slot["end"]))
    extra_after = 0
    for ext in slot.get("extensions", []):
        if avg_temp >= ext["above"]:
            extra_after = max(extra_after, ext.get("extend_after_minutes", 0))
    return end_dt + timedelta(minutes=extra_after)

def _slot_is_active(slot: dict, now: datetime, avg_temp: float) -> bool:
    # Condition d'activation minimale basée sur la moyenne J-1
    min_temp = slot.get("min_temp", None)
    if min_temp is not None and avg_temp < min_temp:
        return False

    start_dt = datetime.combine(now.date(), _parse_time(slot["start"]))
    end_dt   = _compute_end(slot, avg_temp)

    return start_dt <= now <= end_dt

def schedule_wants_pump(temp: float) -> bool | None:
    slots = _load()
    if not slots:
        return None

    # Moyenne J-1 pour les décisions, température actuelle en fallback
    avg_temp = influx_reader.get_avg_temp_yesterday()
    if avg_temp is None:
        print("[WARN] No avg temp available, using current temp as fallback")
        avg_temp = temp

    now = datetime.now()
    for slot in slots:
        if _slot_is_active(slot, now, avg_temp):
            return True

    return None

def compute_today_slots(avg_temp: float) -> list:
    slots = _load()
    result = []
    for slot in slots:
        min_temp = slot.get("min_temp", None)
        activated = min_temp is None or avg_temp >= min_temp

        end_dt   = _compute_end(slot, avg_temp)
        extended = end_dt > datetime.combine(datetime.today(), _parse_time(slot["end"]))

        result.append({
            "start":     slot["start"],
            "end":       end_dt.strftime("%H:%M") if activated else slot["end"],
            "activated": activated,
            "extended":  extended and activated,
        })
    return result