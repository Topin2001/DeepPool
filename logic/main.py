import time
import glob
import sys
from influxdb import InfluxDBClient

# Configuration InfluxDB
client = InfluxDBClient(host='influxdb', port=8086)
DB_NAME = "deeppool"

def read_temp():
    try:
        device_file = glob.glob('/sys/bus/w1/devices/28*/w1_slave')[0]
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if 'YES' in lines[0]:
            temp_c = float(lines[1].split('t=')[1]) / 1000.0
            return temp_c
    except:
        return None

# Attente que la DB soit prête
while True:
    try:
        client.create_database(DB_NAME)
        client.switch_database(DB_NAME)
        break
    except:
        print("⏳ Attente d'InfluxDB...")
        time.sleep(5)

print("🚀 DeepPool commence l'enregistrement...")

while True:
    temp = read_temp()
    if temp:
        json_body = [
            {
                "measurement": "temperature_eau",
                "fields": {"value": temp}
            }
        ]
        client.write_points(json_body)
        print(f"[{time.strftime('%H:%M:%S')}] {temp}°C sauvegardé.")
    
    sys.stdout.flush()
    time.sleep(60) # On enregistre toutes les minutes