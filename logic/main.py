import time
import glob
import sys
import datetime
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient

# --- Configuration ---
GPIO_PIN = 17
TEMP_ON  = 28.0   # activate pump (and LED) above this
TEMP_OFF = 25.0   # deactivate below this
DB_NAME  = "deeppool"

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)
GPIO.output(GPIO_PIN, GPIO.LOW)

# --- InfluxDB setup ---
client = InfluxDBClient(host='influxdb', port=8086)

def read_temp():
    try:
        device_file = glob.glob('/sys/bus/w1/devices/28*/w1_slave')[0]
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if 'YES' in lines[0]:
            return float(lines[1].split('t=')[1]) / 1000.0
    except Exception as e:
        print(f"[WARN] Sensor read failed: {e}")
    return None

def set_pump(active: bool):
    GPIO.output(GPIO_PIN, GPIO.HIGH if active else GPIO.LOW)
    state = "ON" if active else "OFF"
    print(f"[PUMP] {state}")

# Wait for InfluxDB
while True:
    try:
        client.create_database(DB_NAME)
        client.switch_database(DB_NAME)
        print("[INFO] InfluxDB connected.")
        break
    except Exception as e:
        print(f"[INFO] Waiting for InfluxDB... ({e})")
        time.sleep(10)

print("🚀 DeepPool starting...")

pump_active = False

try:
    while True:
        temp = read_temp()
        if temp is not None:
            now = datetime.datetime.now(datetime.UTC)

            # Hysteresis: only change state when crossing the thresholds
            if not pump_active and temp >= TEMP_ON:
                pump_active = True
                set_pump(True)
            elif pump_active and temp <= TEMP_OFF:
                pump_active = False
                set_pump(False)

            client.write_points([
                {
                    "measurement": "temperature_eau",
                    "time": now.isoformat() + "Z",
                    "fields": {"value": temp}
                },
                {
                    "measurement": "etat_pompe",
                    "time": now.isoformat() + "Z",
                    "fields": {
                        "active": pump_active,
                        "value": int(pump_active)
                    }
                }
            ])
            print(f"[{now.strftime('%H:%M:%S')}] {temp:.1f}°C — pompe {'ON' if pump_active else 'OFF'}")

        sys.stdout.flush()
        time.sleep(60)

except KeyboardInterrupt:
    print("\n[INFO] Shutting down...")
finally:
    GPIO.cleanup()