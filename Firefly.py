#!/usr/bin/env python3
# Firefly.py - firefly class
import random

# Setup constants
move_frequency_min: int = 500
move_frequency_max: int = 5000
on_time: float = 0.1
min_off_time: int = 1000
max_off_time: int = 2000

OFF = (0, 0, 0)


class Firefly:
    def __init__(self, strand_pixels, on_color, location_max):
        self.next_move_clock = move_frequency_min

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
        self.strand_pixels[self.location] = OFF
        self.location += (self.direction % self.location_max)

    def update(self, clock):
        if clock > self.next_move_clock:
            self.next_move_clock = clock + random.randrange(self.move_frequency_min, self.move_frequency_maxo)
            self.move()

        # Ensure location is within bounds, and direction is facing the right way
        if self.location <= 0:
            self.location = 0
            self.direction = 1
        elif self.direction >= self.location_max:
            self.location = self.location_max - 1
            self.direction = -1
