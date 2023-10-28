#!/usr/bin/env python3
"""code.py - python code to drive proton pack hardware"""
import atexit
import random
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
STRAND_PIN = board.A0
STRAND_LENGTH: int = 50
STRAND_BRIGHTNESS: float = 0.1
# balance the colors better so white doesn't appear blue-tinged
BRIGHTNESS_LEVELS = (0.25, 0.3, 0.15)

# Length of various timers
# Integers are in microseconds (1000ths)
MOVE_FREQUENCY_MIN: int = 500
MOVE_FREQUENCY_MAX: int = 5000
STRAND_BLINK_PATTERN = [50, 300, 100, 200, 50]
STRAND_MIN_OFF_TIME: int = 1000
STRAND_MAX_OFF_TIME: int = 2000
STRAND_BLINK_MAX: int = 2
STRAND_INIT_DELAY: float = 0.2

# No user config below this point

if supervisor.runtime.serial_connected:
    print("Ƹ̵̡Ӝ̵̨̄Ʒ firefly - github.com/algrym/firefly/code.py -", version.__version__)
    print(f" - Adafruit FancyLed v{fancyled.__version__}")

# Color constants
RED = fancyled.gamma_adjust(fancyled.CRGB(255, 0, 0), brightness=BRIGHTNESS_LEVELS).pack()
ORANGE = fancyled.gamma_adjust(fancyled.CRGB(255, 165, 0), brightness=BRIGHTNESS_LEVELS).pack()
YELLOW = fancyled.gamma_adjust(fancyled.CRGB(255, 255, 0), brightness=BRIGHTNESS_LEVELS).pack()
GREEN = fancyled.gamma_adjust(fancyled.CRGB(0, 255, 0), brightness=BRIGHTNESS_LEVELS).pack()
FIREFLY_GREEN = fancyled.gamma_adjust(
    fancyled.CRGB(150, 255, 100), brightness=BRIGHTNESS_LEVELS).pack()
BLUE = fancyled.gamma_adjust(fancyled.CRGB(0, 0, 255), brightness=BRIGHTNESS_LEVELS).pack()
PURPLE = fancyled.gamma_adjust(fancyled.CRGB(128, 0, 128), brightness=BRIGHTNESS_LEVELS).pack()
WHITE = fancyled.gamma_adjust(fancyled.CRGB(255, 255, 255), brightness=BRIGHTNESS_LEVELS).pack()
OFF = (0, 0, 0)

color_wheel = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE]


def all_off():
    """callback to turn everything off on exit"""
    if supervisor.runtime.serial_connected:
        print(' - Watchdog: standing down.')
    watch_dog.deinit()
    if supervisor.runtime.serial_connected:
        print(' - Exiting: setting all pixels off.')
    neopixel.NeoPixel(STRAND_PIN, STRAND_LENGTH).fill(OFF)
    supervisor.reload()


# Setup hardware watchdog in case things go wrong
watch_dog = microcontroller.watchdog
watch_dog.timeout = 5
watch_dog.mode = watchdog.WatchDogMode.RESET
if supervisor.runtime.serial_connected:
    print(f' - Watchdog: feed me every {watch_dog.timeout} seconds or face {watch_dog.mode}')

# turn everything off on exit
atexit.register(all_off)


def main_event_loop():
    """For CircuitPython optimization, this is just the primary loop
    of the script tucked into one big fat function.
    We also pull some global vars in so now they're function-local.

    It turns out that fetching global vars is expensive.

    Before:
     - Running 271s at 11340.1 loops/second

    After:
     - Running 320s at 39404.7 loops/second
    """

    # setup onboard LED
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    # setup Neopixel strand
    if supervisor.runtime.serial_connected:
        print(f' - NeoPixel strand size {STRAND_LENGTH} on {STRAND_PIN}')
    strand_pixels = neopixel.NeoPixel(STRAND_PIN, STRAND_LENGTH)

    if supervisor.runtime.serial_connected:
        print(' - Running LED test.')
    for c in color_wheel:
        strand_pixels.fill(c)
        watch_dog.feed()
        time.sleep(STRAND_INIT_DELAY)
    strand_pixels.fill(OFF)

    # Initialize counters and clocks
    next_move_clock: int = 0
    next_strand_clock: int = 0
    next_stat_clock: int = supervisor.ticks_ms() + 10000
    strand_direction: int = 1
    strand_cursor: int = random.randrange(0, len(strand_pixels))
    start_time: int = int(time.time())
    last_loop_time: int = start_time
    loop_count: int = 0
    strand_blink_count: int = 0

    if supervisor.runtime.serial_connected:
        print(' - Entering main event loop.')

    while True:
        clock = supervisor.ticks_ms()
        watch_dog.feed()
        led.value = not led.value
        loop_count += 1

        # Print the average runs per second ever 10secs
        if clock > next_stat_clock:
            next_stat_clock: int = clock + 10000
            if supervisor.runtime.serial_connected:
                print(
                    f" - Running {time.time() - start_time}s at {loop_count / (time.time() - last_loop_time)} loops/second")
            loop_count: int = 0
            last_loop_time = int(time.time())

        # Flicker pixels if clock is expired
        if clock > next_strand_clock:
            # If there's still blink pattern to use, do so.
            #  Otherwise reset
            if strand_blink_count < len(STRAND_BLINK_PATTERN):
                next_strand_clock = clock + STRAND_BLINK_PATTERN[strand_blink_count]
                strand_blink_count += 1
            else:
                next_strand_clock = clock + random.randrange(STRAND_MIN_OFF_TIME, STRAND_MAX_OFF_TIME)
                strand_blink_count = 0

            # Handling blinking the light
            if strand_pixels[strand_cursor] == OFF:
                strand_pixels[strand_cursor] = FIREFLY_GREEN
            else:
                strand_pixels[strand_cursor] = OFF
            continue  # Don't move the firefly while in the flash pattern

        # Adjust location if clock is expired
        if clock > next_move_clock:
            next_move_clock = clock + random.randrange(MOVE_FREQUENCY_MIN, MOVE_FREQUENCY_MAX)

            # Blank all the pixels
            strand_pixels.fill(OFF)
            strand_blink_count = 0

            # Decide if we switch direction
            if random.randrange(0, 2) == 0:
                strand_direction: int = strand_direction * int(-1)

            # Bounce if the cursor is at the end of the strand
            if strand_cursor == 0:
                strand_direction = 1
            elif strand_cursor >= (len(strand_pixels) - 1):
                strand_direction = -1

            # Move the firefly
            if supervisor.runtime.serial_connected:
                print(f'   - Moving cursor={strand_cursor} direction={strand_direction} max={len(strand_pixels)}')
            strand_cursor = (strand_cursor + strand_direction) % len(strand_pixels)


if __name__ == "__main__":
    main_event_loop()
