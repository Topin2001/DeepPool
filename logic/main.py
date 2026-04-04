import time
import sys
import signal
import temp_sensor
import pump_control
import db_client
import controller

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

print("🚀 DeepPool starting...")

try:
    while True:
        temp = temp_sensor.read_temp()

        if temp is not None:
            pump_state = controller.resolve_pump_state(temp=temp)
            pump_control.set_pump(pump_state)
            db_client.write(temp, pump_state)
            print(f"[{time.strftime('%H:%M:%S')}] {temp:.1f}°C — pompe {'ON' if pump_state else 'OFF'}")

        sys.stdout.flush()
        time.sleep(60)

except KeyboardInterrupt:
    pass
finally:
    pump_control.cleanup()
    db_client.close()