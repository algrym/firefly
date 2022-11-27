#!/usr/bin/env python3
# code.py
import atexit
import random
import sys
import time

import adafruit_fancyled.adafruit_fancyled as fancyled
import board
import digitalio
import microcontroller
import neopixel
import supervisor
import watchdog

import version

# Config variables
strand_pin = board.D21
strand_length: int = 50
strand_brightness: float = 0.1
brightness_levels = (0.25, 0.3, 0.15)  # balance the colors better so white doesn't appear blue-tinged

# Length of various timers
# Floats are in seconds
# Integers are in microseconds (1000ths)
move_frequency_min: int = 500
move_frequency_max: int = 5000
strand_on_time: float = 0.1
strand_min_off_time: int = 1000
strand_max_off_time: int = 2000

# No user config below this point

print("Ƹ̵̡Ӝ̵̨̄Ʒ firefly - github.com/algrym/firefly/code.py -", version.__version__)
print(f" - Adafruit FancyLed v{fancyled.__version__}")

# Color constants
RED = fancyled.gamma_adjust(fancyled.CRGB(255, 0, 0), brightness=brightness_levels).pack()
ORANGE = fancyled.gamma_adjust(fancyled.CRGB(255, 165, 0), brightness=brightness_levels).pack()
YELLOW = fancyled.gamma_adjust(fancyled.CRGB(255, 255, 0), brightness=brightness_levels).pack()
GREEN = fancyled.gamma_adjust(fancyled.CRGB(0, 255, 0), brightness=brightness_levels).pack()
FIREFLY_GREEN = fancyled.gamma_adjust(fancyled.CRGB(150, 255, 100), brightness=brightness_levels).pack()
BLUE = fancyled.gamma_adjust(fancyled.CRGB(0, 0, 255), brightness=brightness_levels).pack()
PURPLE = fancyled.gamma_adjust(fancyled.CRGB(128, 0, 128), brightness=brightness_levels).pack()
WHITE = fancyled.gamma_adjust(fancyled.CRGB(255, 255, 255), brightness=brightness_levels).pack()
OFF = (0, 0, 0)

color_wheel = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE]


def all_off():
    # callback to turn everything off on exit
    print(' - Watchdog: standing down.')
    watch_dog.deinit()
    print(' - Exiting: setting all pixels off.')
    strand_pixels.fill(OFF)
    sys.exit(0)


# Setup hardware watchdog in case things go wrong
watch_dog = microcontroller.watchdog
watch_dog.timeout = 5
watch_dog.mode = watchdog.WatchDogMode.RESET
print(f' - Watchdog: feed me every {watch_dog.timeout} seconds or face {watch_dog.mode}')

# turn everything off on exit
atexit.register(all_off)

# setup onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# setup strand NEOPIXELs
print(f' - NeoPixel strand size {strand_length} on {strand_pin}')
strand_pixels = neopixel.NeoPixel(strand_pin, strand_length)
# brightness=strand_brightness)

next_move_clock: int = 0
next_strand_clock: int = 0
next_stat_clock: int = 0
strand_direction: int = 1
strand_cursor: int = 0
start_time: int = time.time()
loop_count: int = 0

print(' - Running LED test.')
for c in color_wheel:
    strand_pixels.fill(c)
    watch_dog.feed()
    time.sleep(strand_on_time)
strand_pixels.fill(OFF)

print(' - Entering main event loop.')
while True:
    clock = supervisor.ticks_ms()
    loop_count += 1

    # Print the average runs per second ever 10secs
    if clock > next_stat_clock:
        next_stat_clock: int = clock + 10000
        print(f" - Loop #{loop_count} at {loop_count / (time.time() - start_time)} loops/second")

    # Adjust location if clock is expired
    if clock > next_move_clock:
        next_move_clock = clock + random.randrange(move_frequency_min, move_frequency_max)

        # Blank all the pixels
        strand_pixels.fill(OFF)

        # Decide if we switch direction
        if random.randrange(0, 2) == 0:
            strand_direction: int = strand_direction * int(-1)

        # Bounce if the cursor is at the end of the strand
        if strand_cursor == 0:
            strand_direction = 1
        elif strand_cursor >= (len(strand_pixels) - 1):
            strand_direction = -1

        # Move the firefly
        print(f'   - Moving cursor={strand_cursor} direction={strand_direction} max={len(strand_pixels)}')
        strand_cursor = (strand_cursor + strand_direction) % len(strand_pixels)

    # Flicker pixels if clock is expired
    if clock > next_strand_clock:
        next_strand_clock = clock + random.randrange(strand_min_off_time, strand_max_off_time)

        strand_pixels[strand_cursor] = FIREFLY_GREEN
        time.sleep(strand_on_time)
        strand_pixels[strand_cursor] = OFF
        time.sleep(3 * strand_on_time)
        strand_pixels[strand_cursor] = FIREFLY_GREEN
        time.sleep(strand_on_time)
        strand_pixels[strand_cursor] = OFF

    # Increment heartbeat LED and feed the watchdog
    led.value = not led.value
    watch_dog.feed()
    time.sleep(0.1)
