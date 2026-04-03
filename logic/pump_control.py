import RPi.GPIO as GPIO

GPIO_PIN = 17

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, GPIO.LOW)

def set_pump(active: bool):
    GPIO.output(GPIO_PIN, GPIO.HIGH if active else GPIO.LOW)
    print(f"[PUMP] {'ON' if active else 'OFF'}")

def cleanup():
    GPIO.cleanup()