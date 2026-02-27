import time
import glob
import sys

def get_temp_sensor_path():
    """Trouve dynamiquement le chemin du capteur 1-Wire."""
    try:
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28*')
        if not device_folders:
            return None
        return device_folders[0] + '/w1_slave'
    except Exception as e:
        print(f"Erreur lors de la recherche du capteur : {e}")
        return None

def read_temp():
    """Lit la température et gère les erreurs de lecture."""
    path = get_temp_sensor_path()
    if not path:
        return None, "Capteur introuvable (Vérifiez le câblage et l'activation 1-Wire)"

    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        
        # Vérification du CRC (Cyclic Redundancy Check)
        if 'YES' not in lines[0]:
            return None, "Donnée corrompue (Erreur CRC)"

        # Extraction de la température
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c, None
    except Exception as e:
        return None, f"Erreur de lecture du fichier : {e}"
    
    return None, "Format de fichier inconnu"

# --- BOUCLE PRINCIPALE ---
print("--- DeepPool : Surveillance Température (Mode Console) ---")

while True:
    temperature, error = read_temp()
    
    if temperature is not None:
        # On affiche la température avec l'heure
        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] Température Eau : {temperature:.2f}°C")
    else:
        print(f"⚠️ {error}")

    # Forcer l'affichage dans les logs Docker immédiatement
    sys.stdout.flush()
    
    # Pause de 10 secondes pour le test (plus court pour valider rapidement)
    time.sleep(10)