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

# CORS — sera restreint à l'URL du site React en prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modèles ---

class ConfigUpdate(BaseModel):
    temp_on:  Optional[float] = None
    temp_off: Optional[float] = None

class OverrideUpdate(BaseModel):
    state: Optional[bool] = None  # True=ON, False=OFF, None=auto

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

    return {
        "temperature": temp,
        "pump":        pump_state,
        "override":    override["state"],
    }

# --- Température ---

@app.get("/temperature")
def get_temperature(user: str = Depends(auth.get_current_user)):
    return {"data": influx.get_temperature_history()}

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