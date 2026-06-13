import json
import os
from datetime import datetime, time, timedelta, date

SCHEDULE_PATH = os.environ.get("SCHEDULE_PATH", "/config/schedule.json")

def _load() -> list:
    try:
        with open(SCHEDULE_PATH, 'r') as f:
            data = json.load(f)
            return data.get("schedule", [])
    except:
        return []

def _parse_time(t_str: str) -> time:
    h, m = t_str.split(":")
    return time(int(h), int(m))

def _compute_end(slot: dict, avg_temp: float, end_date: date) -> datetime:
    end_dt = datetime.combine(end_date, _parse_time(slot["end"]))
    extra_after = 0
    for ext in slot.get("extensions", []):
        if avg_temp >= ext["above"]:
            extra_after = max(extra_after, ext.get("extend_after_minutes", 0))
    return end_dt + timedelta(minutes=extra_after)

def compute_today_slots(avg_temp: float | None) -> list:
    slots    = _load()
    ref_temp = avg_temp if avg_temp is not None else 0.0
    result   = []
    today    = datetime.now().date()

    for slot in slots:
        min_temp  = slot.get("min_temp", None)
        activated = min_temp is None or ref_temp >= min_temp

        start_t = _parse_time(slot["start"])
        end_t   = _parse_time(slot["end"])
        overnight = end_t <= start_t

        end_date = today + timedelta(days=1) if overnight else today
        end_dt   = _compute_end(slot, ref_temp, end_date)
        extended = end_dt > datetime.combine(end_date, end_t)

        end_label = end_dt.strftime("%H:%M")
        if overnight and activated:
            end_label += " (+1j)"

        result.append({
            "start":     slot["start"],
            "end":       end_label if activated else slot["end"],
            "activated": activated,
            "extended":  extended and activated,
        })

    return result