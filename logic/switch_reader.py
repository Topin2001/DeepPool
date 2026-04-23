import RPi.GPIO as GPIO
import config

def setup():
    cfg = config.load()
    GPIO.setup(cfg["gpio_pin_sw_on"],  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(cfg["gpio_pin_sw_off"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def read_manual() -> bool | None:
    cfg = config.load()
    sw_on  = GPIO.input(cfg["gpio_pin_sw_on"])
    sw_off = GPIO.input(cfg["gpio_pin_sw_off"])
    if sw_on and not sw_off:
        return True
    if sw_off and not sw_on:
        return False
    return None