"""
physics.py — Physics constants and helper functions.
Modify values here to change how the game feels.
"""
from core.settings import (
    GRAVITY, TERMINAL_VELOCITY, GROUND_FRICTION, AIR_FRICTION
)


def apply_gravity(vel_y, dt=1):
    """Apply gravity to vertical velocity."""
    vel_y += GRAVITY * dt
    if vel_y > TERMINAL_VELOCITY:
        vel_y = TERMINAL_VELOCITY
    return vel_y


def apply_friction(vel_x, on_ground):
    """Apply friction to horizontal velocity."""
    friction = GROUND_FRICTION if on_ground else AIR_FRICTION
    return vel_x * friction


def move_toward(current, target, speed):
    """Move a value toward a target at given speed."""
    if current < target:
        return min(current + speed, target)
    elif current > target:
        return max(current - speed, target)
    return current
