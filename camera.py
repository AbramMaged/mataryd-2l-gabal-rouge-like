"""
camera.py — Camera system with smooth follow and screen shake.
"""
import random
import math
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SHAKE_INTENSITY


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.lerp_speed = 0.1

        # Screen shake
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0

    def follow(self, target_x, target_y, level_width, level_height):
        """Smoothly follow a target position."""
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2

        # Clamp to level bounds
        self.target_x = max(0, min(self.target_x, level_width - SCREEN_WIDTH))
        self.target_y = max(0, min(self.target_y, level_height - SCREEN_HEIGHT))

        # Smooth lerp
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed

    def add_shake(self, intensity, duration):
        """Trigger screen shake."""
        self.shake_intensity = intensity * SCREEN_SHAKE_INTENSITY
        self.shake_duration = duration
        self.shake_timer = duration

    def update(self):
        """Update shake offset."""
        if self.shake_timer > 0:
            progress = self.shake_timer / max(self.shake_duration, 1)
            intensity = self.shake_intensity * progress
            angle = random.uniform(0, math.pi * 2)
            self.shake_x = math.cos(angle) * intensity
            self.shake_y = math.sin(angle) * intensity
            self.shake_timer -= 1
        else:
            self.shake_x = 0
            self.shake_y = 0

    def apply(self, x, y):
        """Convert world coordinates to screen coordinates."""
        return (
            x - self.x + self.shake_x,
            y - self.y + self.shake_y
        )

    def get_offset(self):
        return (self.x - self.shake_x, self.y - self.shake_y)
