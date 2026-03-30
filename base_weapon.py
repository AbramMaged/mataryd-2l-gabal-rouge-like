"""
base_weapon.py — Base class for all weapons.
"""


class BaseWeapon:
    """Base weapon with common stats and methods."""

    def __init__(self, name, damage, fire_rate, reload_time,
                 ammo_capacity, bullet_speed, bullet_size):
        self.name = name
        self.base_damage = damage
        self.damage = damage
        self.fire_rate = fire_rate
        self.reload_time = reload_time
        self.ammo_capacity = ammo_capacity
        self.current_ammo = ammo_capacity
        self.bullet_speed = bullet_speed
        self.bullet_size = bullet_size

        self.fire_timer = 0
        self.reload_timer = 0
        self.is_reloading = False

        # Upgrade multipliers
        self.damage_mult = 1.0
        self.ammo_bonus = 0
        self.reload_speed_mult = 1.0
        self.fire_rate_mult = 1.0

    def can_fire(self):
        return (self.fire_timer <= 0 and
                self.current_ammo > 0 and
                not self.is_reloading)

    def fire(self):
        """Fire the weapon. Returns True if successful."""
        if not self.can_fire():
            return False
        self.current_ammo -= 1
        self.fire_timer = int(self.fire_rate / self.fire_rate_mult)
        return True

    def start_reload(self):
        if self.is_reloading:
            return
        if self.current_ammo >= self.get_max_ammo():
            return
        self.is_reloading = True
        self.reload_timer = int(self.reload_time / self.reload_speed_mult)

    def update(self):
        if self.fire_timer > 0:
            self.fire_timer -= 1

        if self.is_reloading:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.current_ammo = self.get_max_ammo()
                self.is_reloading = False

    def get_damage(self):
        return int(self.damage * self.damage_mult)

    def get_max_ammo(self):
        return self.ammo_capacity + self.ammo_bonus

    def reset(self):
        self.current_ammo = self.get_max_ammo()
        self.fire_timer = 0
        self.reload_timer = 0
        self.is_reloading = False
