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
    physical_request: bool | None = None,
    web_override: bool | None = None,
    schedule_request: bool | None = None,
) -> bool:
    cfg = config.load()

    # 1. Switch physique — priorité absolue
    if physical_request is not None:
        return physical_request

    # 2. Override web — forcé depuis le site
    if web_override is not None:
        return web_override

    # 3. Planning horaire
    if schedule_request is not None:
        return schedule_request

    # 4. Température — fallback automatique
    return _temp_wants_pump(temp, cfg["temp_on"], cfg["temp_off"])