import time
from influxdb import InfluxDBClient

DB_NAME = "deeppool"
_client = None

def connect():
    global _client
    _client = InfluxDBClient(host='influxdb', port=8086)
    while True:
        try:
            _client.create_database(DB_NAME)
            _client.switch_database(DB_NAME)
            print("[INFO] InfluxDB connected.")
            break
        except Exception as e:
            print(f"[INFO] Waiting for InfluxDB... ({e})")
            time.sleep(10)

def write(temp: float, pump_active: bool):
    _client.write_points([
        {
            "measurement": "temperature_eau",
            "fields": {"value": temp}
        },
        {
            "measurement": "etat_pompe",
            "fields": {"value": int(pump_active)}
        }
    ])