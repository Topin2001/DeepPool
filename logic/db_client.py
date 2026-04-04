import os
import time
from influxdb_client import InfluxDBClient, WriteOptions

_client  = None
_write_api = None

def connect():
    global _client, _write_api
    url    = os.environ["INFLUXDB_URL"]
    token  = os.environ["INFLUXDB_TOKEN"]
    org    = os.environ["INFLUXDB_ORG"]

    while True:
        try:
            _client = InfluxDBClient(url=url, token=token, org=org)
            _client.ping()
            _write_api = _client.write_api(write_options=WriteOptions(batch_size=1))
            print("[INFO] InfluxDB connected.")
            break
        except Exception as e:
            print(f"[INFO] Waiting for InfluxDB... ({e})")
            time.sleep(10)

def write(temp: float, pump_active: bool):
    bucket = os.environ["INFLUXDB_BUCKET"]
    org    = os.environ["INFLUXDB_ORG"]
    _write_api.write(
        bucket=bucket,
        org=org,
        record=[
            {
                "measurement": "temperature_eau",
                "fields": {"value": temp}
            },
            {
                "measurement": "etat_pompe",
                "fields": {"value": int(pump_active)}
            }
        ]
    )

def close():
    if _client:
        _client.close()