import time
import sys
import signal
import json
import os
import config
import temp_sensor
import pump_control
import db_client
import controller
import switch_reader
import scheduler
import override_reader

OVERRIDE_PATH = os.environ.get("OVERRIDE_PATH", "/config/override.json")

def handle_shutdown(signum, frame):
    print("\n[INFO] Shutting down...")
    pump_control.cleanup()
    db_client.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# --- Setup ---
pump_control.setup()
db_client.connect()
cfg = config.load()

print("🚀 DeepPool starting...")

FAST_INTERVAL = cfg.get("fast_interval_seconds", 5)
SLOW_INTERVAL = cfg.get("loop_interval_seconds", 60)

last_slow = 0
last_temp = None  # dernière température connue

try:
    while True:
        now = time.time()
        cfg = config.load()

        # --- Boucle rapide : contrôle pompe ---
        physical  = switch_reader.read_manual()
        scheduled = scheduler.schedule_wants_pump(last_temp or 0.0)

        # Mettre à jour l'état physique dans override.json
        override_data = override_reader.read_override()
        override_data["physical"] = physical
        try:
            with open(OVERRIDE_PATH, 'w') as f:
                json.dump(override_data, f, indent=4)
        except Exception as e:
            print(f"[WARN] Could not write physical state: {e}")

        web_over = override_data.get("web", None)

        pump_state = controller.resolve_pump_state(
            temp=last_temp or 0.0,
            physical_request=physical,
            web_override=web_over,
            schedule_request=scheduled,
        )
        pump_control.set_pump(pump_state)

        # --- Boucle lente : température + BDD ---
        if now - last_slow >= SLOW_INTERVAL:
            temp = temp_sensor.read_temp()
            if temp is not None:
                last_temp = temp
                db_client.write(temp, pump_state)

                if physical is not None:
                    mode = f"physique {'ON' if physical else 'OFF'}"
                elif web_over is not None:
                    mode = f"override web {'ON' if web_over else 'OFF'}"
                elif scheduled is not None:
                    mode = "planning"
                else:
                    mode = "auto temp"

                print(f"[{time.strftime('%H:%M:%S')}] {temp:.1f}°C — pompe {'ON' if pump_state else 'OFF'} ({mode})")

            last_slow = now

        sys.stdout.flush()
        time.sleep(FAST_INTERVAL)

except KeyboardInterrupt:
    pass
finally:
    pump_control.cleanup()
    db_client.close()