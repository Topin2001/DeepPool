# --- Hysteresis thresholds ---
TEMP_ON  = 28.0
TEMP_OFF = 25.0

_pump_active = False

def _temp_wants_pump(temp: float) -> bool:
    global _pump_active
    if not _pump_active and temp >= TEMP_ON:
        _pump_active = True
    elif _pump_active and temp <= TEMP_OFF:
        _pump_active = False
    return _pump_active

def resolve_pump_state(
    temp: float,
    schedule_request: bool | None = None,
    manual_request: bool | None = None
) -> bool:
    if manual_request is not None:
        return manual_request
    if schedule_request is not None:
        return schedule_request
    return _temp_wants_pump(temp)