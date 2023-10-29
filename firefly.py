#!/usr/bin/env python3
"""firefly.py - firefly class"""
import random

# Setup constants
MOVE_FREQUENCY_MIN: int = 500
MOVE_FREQUENCY_MAX: int = 5000
ON_TIME: float = 0.1
MIN_OFF_TIME: int = 1000
MAX_OFF_TIME: int = 2000

OFF = 0


class FireFly:
    """firefly.py - firefly class"""

    def __init__(self, strand_pixels, on_color, location_max):
        self.next_move_clock = MOVE_FREQUENCY_MIN

        # Copy arguments into instance attributes
        self.strand_pixels = strand_pixels
        self.location_max = location_max
        self.on_color = on_color

        # Set a random direction and location
        self.location = random.randrange(0, location_max)
        self.direction = 1
        if (random.randrange(0, 10) % 2) == 0:
            self.direction = -1

        # perform initial update
        self.update(0)

    def move(self):
        """move the firefly to a new location in the right direction"""
        self.strand_pixels[self.location] = OFF
        self.location += (self.direction % self.location_max)

    def update(self, clock):
        """increment internal clocks and bounds-check"""
        if clock > self.next_move_clock:
            self.next_move_clock = \
                clock + random.randrange(MOVE_FREQUENCY_MIN,
                                         MOVE_FREQUENCY_MAX)
            self.move()

        # Ensure location is within bounds, and direction is facing the right way
        if self.location <= 0:
            self.location = 0
            self.direction = 1
        elif self.direction >= self.location_max:
            self.location = self.location_max - 1
            self.direction = -1
