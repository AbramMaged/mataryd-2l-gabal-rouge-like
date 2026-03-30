"""
input_handler.py — Abstracts raw Pygame input into game actions.
Uses keybinds from settings so controls are remappable.
"""
import pygame
from core.settings import KEYBINDS


class InputHandler:
    def __init__(self):
        self.keys_pressed = {}
        self.keys_just_pressed = {}
        self.keys_just_released = {}
        self.mouse_pos = (0, 0)
        self.mouse_pressed = [False, False, False]
        self.mouse_just_pressed = [False, False, False]
        self._prev_keys = set()
        self._prev_mouse = [False, False, False]

    def update(self):
        """Call once per frame before checking inputs."""
        keys = pygame.key.get_pressed()
        current_keys = set(k for k in range(len(keys)) if keys[k])

        self.keys_just_pressed = current_keys - self._prev_keys
        self.keys_just_released = self._prev_keys - current_keys
        self.keys_pressed = current_keys
        self._prev_keys = current_keys.copy()

        self.mouse_pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()
        self.mouse_just_pressed = [
            mouse[i] and not self._prev_mouse[i] for i in range(3)
        ]
        self.mouse_pressed = list(mouse)
        self._prev_mouse = list(mouse)

    # ─── Action helpers ───────────────────────────────────
    def is_held(self, action):
        key = KEYBINDS.get(action)
        if key is None:
            return False
        return key in self.keys_pressed

    def is_just_pressed(self, action):
        key = KEYBINDS.get(action)
        if key is None:
            return False
        return key in self.keys_just_pressed

    def jump_pressed(self):
        return (
            self.is_just_pressed("jump") or
            self.is_just_pressed("jump_alt")
        )

    def shoot_pressed(self):
        return self.mouse_pressed[0]

    def shoot_just_pressed(self):
        return self.mouse_just_pressed[0]

    def parry_just_pressed(self):
        return self.mouse_just_pressed[2] or self.is_just_pressed("parry")

    def get_mouse_pos(self):
        return self.mouse_pos
