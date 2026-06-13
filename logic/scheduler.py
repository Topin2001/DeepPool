import json
import os
from datetime import datetime, time, timedelta, date
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

def _compute_end(slot: dict, avg_temp: float, end_date: date) -> datetime:
    end_dt = datetime.combine(end_date, _parse_time(slot["end"]))
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

    start_t = _parse_time(slot["start"])
    end_t   = _parse_time(slot["end"])
    overnight = end_t <= start_t

    if overnight:
        # Fenêtre 1 : commencée hier soir, se termine aujourd'hui
        start_dt_1 = datetime.combine(now.date() - timedelta(days=1), start_t)
        end_dt_1   = _compute_end(slot, avg_temp, now.date())
        if start_dt_1 <= now <= end_dt_1:
            return True

        # Fenêtre 2 : commence ce soir, se termine demain
        start_dt_2 = datetime.combine(now.date(), start_t)
        end_dt_2   = _compute_end(slot, avg_temp, now.date() + timedelta(days=1))
        if start_dt_2 <= now <= end_dt_2:
            return True

        return False
    else:
        start_dt = datetime.combine(now.date(), start_t)
        end_dt   = _compute_end(slot, avg_temp, now.date())
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
    today = datetime.now().date()

    for slot in slots:
        min_temp  = slot.get("min_temp", None)
        activated = min_temp is None or avg_temp >= min_temp

        start_t = _parse_time(slot["start"])
        end_t   = _parse_time(slot["end"])
        overnight = end_t <= start_t

        end_date = today + timedelta(days=1) if overnight else today
        end_dt   = _compute_end(slot, avg_temp, end_date)
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