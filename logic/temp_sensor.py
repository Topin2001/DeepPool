import glob

def read_temp() -> float | None:
    try:
        device_file = glob.glob('/sys/bus/w1/devices/28*/w1_slave')[0]
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if 'YES' in lines[0]:
            return float(lines[1].split('t=')[1]) / 1000.0
    except Exception as e:
        print(f"[WARN] Sensor read failed: {e}")
    return None