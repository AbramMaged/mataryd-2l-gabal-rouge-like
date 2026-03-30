"""
deagle.py — Desert Eagle weapon.
High damage, single target, fast fire rate, quick reload.
"""
from weapons.base_weapon import BaseWeapon
from core.settings import (
    DEAGLE_DAMAGE, DEAGLE_FIRE_RATE, DEAGLE_RELOAD_TIME,
    DEAGLE_AMMO_CAPACITY, DEAGLE_BULLET_SPEED, DEAGLE_BULLET_SIZE
)


class Deagle(BaseWeapon):
    def __init__(self):
        super().__init__(
            name="Deagle",
            damage=DEAGLE_DAMAGE,
            fire_rate=DEAGLE_FIRE_RATE,
            reload_time=DEAGLE_RELOAD_TIME,
            ammo_capacity=DEAGLE_AMMO_CAPACITY,
            bullet_speed=DEAGLE_BULLET_SPEED,
            bullet_size=DEAGLE_BULLET_SIZE,
        )
        self.piercing = False  # Upgrade: bullets pass through 1 enemy

    def get_projectile_config(self):
        """Return config for projectile creation."""
        return {
            'type': 'bullet',
            'damage': self.get_damage(),
            'speed': self.bullet_speed,
            'size': self.bullet_size,
            'piercing': self.piercing,
            'count': 1,
            'spread': 0,
        }
