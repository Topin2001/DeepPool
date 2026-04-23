import config

_pump_active = False

def _temp_wants_pump(temp: float, temp_on: float, temp_off: float) -> bool:
    global _pump_active
    if not _pump_active and temp >= temp_on:
        _pump_active = True
    elif _pump_active and temp <= temp_off:
        _pump_active = False
    return _pump_active

def resolve_pump_state(
    temp: float,
    schedule_request: bool | None = None,
    manual_request: bool | None = None
) -> bool:
    cfg = config.load()
    if manual_request is not None:
        return manual_request
    if schedule_request is not None:
        return schedule_request
    return _temp_wants_pump(temp, cfg["temp_on"], cfg["temp_off"])