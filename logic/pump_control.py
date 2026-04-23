import RPi.GPIO as GPIO
import switch_reader
import config

_gpio_pin = None
_is_setup = False
_current_state = None

def setup():
    global _gpio_pin, _is_setup
    cfg = config.load()
    _gpio_pin = cfg["gpio_pin_pump"]
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(_gpio_pin, GPIO.OUT)
    GPIO.output(_gpio_pin, GPIO.LOW)
    switch_reader.setup()
    _is_setup = True

def set_pump(active: bool):
    global _current_state
    if active == _current_state:
        return
    GPIO.output(_gpio_pin, GPIO.HIGH if active else GPIO.LOW)
    print(f"[PUMP] {'ON' if active else 'OFF'}")
    _current_state = active

def cleanup():
    global _is_setup
    if _is_setup:
        GPIO.cleanup()
        _is_setup = False