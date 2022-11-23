#!/usr/bin/env python3
# code.py
import time
import board
import neopixel
import version
import digitalio

print("Ƹ̵̡Ӝ̵̨̄Ʒ firefly - github.com/algrym/firefly/code.py -", version.__version__)

FIREFLY_GREEN = (0, 255, 175)
OFF = (0, 0, 0)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = 0.1
    time.sleep(0.1)
    led.value = False
    time.sleep(0.1)
    led.value = 0.1
    time.sleep(0.1)
    led.value = False
    time.sleep(0.8)
