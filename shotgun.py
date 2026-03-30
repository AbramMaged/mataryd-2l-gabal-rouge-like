"""
shotgun.py — Shotgun weapon.
Spread shot, multi-hit, slower fire rate, longer reload.
Stronger than deagle when all pellets connect.
"""
from weapons.base_weapon import BaseWeapon
from core.settings import (
    SHOTGUN_DAMAGE, SHOTGUN_PELLETS, SHOTGUN_SPREAD,
    SHOTGUN_FIRE_RATE, SHOTGUN_RELOAD_TIME,
    SHOTGUN_AMMO_CAPACITY, SHOTGUN_PELLET_SPEED, SHOTGUN_PELLET_SIZE
)


class Shotgun(BaseWeapon):
    def __init__(self):
        super().__init__(
            name="Shotgun",
            damage=SHOTGUN_DAMAGE,
            fire_rate=SHOTGUN_FIRE_RATE,
            reload_time=SHOTGUN_RELOAD_TIME,
            ammo_capacity=SHOTGUN_AMMO_CAPACITY,
            bullet_speed=SHOTGUN_PELLET_SPEED,
            bullet_size=SHOTGUN_PELLET_SIZE,
        )
        self.pellets = SHOTGUN_PELLETS
        self.spread = SHOTGUN_SPREAD  # degrees
        self.extra_pellets = 0  # Upgrade bonus

    def get_projectile_config(self):
        """Return config for projectile creation."""
        return {
            'type': 'pellet',
            'damage': self.get_damage(),
            'speed': self.bullet_speed,
            'size': self.bullet_size,
            'piercing': False,
            'count': self.pellets + self.extra_pellets,
            'spread': self.spread,
        }
