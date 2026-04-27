import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

import auth
import influx
import config_manager

app = FastAPI(title="DeepPool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_HOURS = {6, 12, 24, 48, 72, 168}

# --- Modèles ---

class ConfigUpdate(BaseModel):
    temp_on:  Optional[float] = None
    temp_off: Optional[float] = None

class OverrideUpdate(BaseModel):
    state: Optional[bool] = None

class ScheduleUpdate(BaseModel):
    schedule: list

# --- Auth ---

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != os.environ["API_USERNAME"] or \
       form.password != os.environ["API_PASSWORD"]:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    token = auth.create_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}

# --- Status ---

@app.get("/status")
def get_status(user: str = Depends(auth.get_current_user)):
    temp       = influx.get_latest_temperature()
    pump_state = influx.get_latest_pump_state()
    override   = config_manager.read_override()

    physical = override["physical"]
    web      = override["web"]

    if physical is not None:
        mode = "physique_on" if physical else "physique_off"
    elif web is not None:
        mode = "override_on" if web else "override_off"
    else:
        mode = "auto"

    return {
        "temperature": temp,
        "pump":        pump_state,
        "override":    web,
        "mode":        mode,
    }

# --- Température ---

@app.get("/temperature")
def get_temperature(hours: int = 24, user: str = Depends(auth.get_current_user)):
    if hours not in VALID_HOURS:
        raise HTTPException(status_code=400, detail="Valeur hours invalide (6/12/24/48/72/168)")
    return {"data": influx.get_temperature_history(hours)}

@app.get("/pump/history")
def get_pump_history(hours: int = 24, user: str = Depends(auth.get_current_user)):
    if hours not in VALID_HOURS:
        raise HTTPException(status_code=400, detail="Valeur hours invalide (6/12/24/48/72/168)")
    return {"data": influx.get_pump_history(hours)}

# --- Config ---

@app.get("/config")
def get_config(user: str = Depends(auth.get_current_user)):
    cfg = config_manager.read_config()
    return {
        "temp_on":  cfg["temp_on"],
        "temp_off": cfg["temp_off"],
    }

@app.put("/config")
def update_config(body: ConfigUpdate, user: str = Depends(auth.get_current_user)):
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="Aucune valeur fournie")
    if "temp_on" in update and "temp_off" in update:
        if update["temp_off"] >= update["temp_on"]:
            raise HTTPException(status_code=400, detail="temp_off doit être inférieur à temp_on")
    config_manager.write_config(update)
    return {"message": "Config mise à jour", "data": update}

# --- Override ---

@app.get("/override")
def get_override(user: str = Depends(auth.get_current_user)):
    return config_manager.read_override()

@app.put("/override")
def update_override(body: OverrideUpdate, user: str = Depends(auth.get_current_user)):
    config_manager.write_override(body.state)
    return {"message": "Override mis à jour", "state": body.state}

# --- Schedule ---

@app.get("/schedule")
def get_schedule(user: str = Depends(auth.get_current_user)):
    return config_manager.read_schedule()

@app.put("/schedule")
def update_schedule(body: ScheduleUpdate, user: str = Depends(auth.get_current_user)):
    config_manager.write_schedule({"schedule": body.schedule})
    return {"message": "Planning mis à jour", "schedule": body.schedule}

@app.get("/schedule/today")
def get_schedule_today(user: str = Depends(auth.get_current_user)):
    from scheduler_helper import compute_today_slots
    avg_temp = influx.get_avg_temp_yesterday()
    slots    = compute_today_slots(avg_temp)
    return {
        "avg_temp_yesterday": avg_temp,
        "planned_slots":      slots,
    }