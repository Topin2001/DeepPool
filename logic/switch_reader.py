import RPi.GPIO as GPIO

GPIO_SW_ON  = 23   # SW1 — Marche forcée
GPIO_SW_OFF = 24   # SW2 — Arrêt forcé

def setup():
    GPIO.setup(GPIO_SW_ON,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GPIO_SW_OFF, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def read_manual() -> bool | None:
    sw_on  = GPIO.input(GPIO_SW_ON)
    sw_off = GPIO.input(GPIO_SW_OFF)

    if sw_on and not sw_off:
        return True    # marche forcée
    if sw_off and not sw_on:
        return False   # arrêt forcé
    return None        # auto (les deux OFF, ou les deux ON → ignoré)