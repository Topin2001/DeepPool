import RPi.GPIO as GPIO
import switch_reader

GPIO_PIN = 17
_is_setup = False

def setup():
    global _is_setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, GPIO.LOW)
    switch_reader.setup()
    _is_setup = True

def set_pump(active: bool):
    GPIO.output(GPIO_PIN, GPIO.HIGH if active else GPIO.LOW)
    print(f"[PUMP] {'ON' if active else 'OFF'}")

def cleanup():
    global _is_setup
    if _is_setup:
        GPIO.cleanup()
        _is_setup = False