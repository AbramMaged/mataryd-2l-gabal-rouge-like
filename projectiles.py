"""
projectiles.py — Bullets, pellets, and enemy projectiles.
"""
import pygame
import math
from art.colors import UI_AMMO_BULLET, UI_AMMO_SHELL, MUZZLE_FLASH, ENEMY_GRUNT


class Projectile:
    """A single projectile (bullet, pellet, or enemy bullet)."""

    def __init__(self, x, y, angle, speed, damage, size,
                 is_player=True, piercing=False, proj_type='bullet'):
        self.x = x
        self.y = y
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.damage = damage
        self.size = size
        self.is_player = is_player
        self.piercing = piercing
        self.proj_type = proj_type
        self.alive = True
        self.hit_count = 0
        self.max_hits = 2 if piercing else 1
        self.lifetime = 120  # frames before despawn
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size),
            int(self.y - self.size),
            self.size * 2,
            self.size * 2
        )

    def update(self):
        # Store trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def on_hit(self):
        """Called when projectile hits something."""
        self.hit_count += 1
        if self.hit_count >= self.max_hits:
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.x, self.y)

        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            tsx, tsy = camera.apply(tx, ty)
            alpha = (i + 1) / len(self.trail) * 0.5
            trail_size = max(1, int(self.size * alpha))
            if self.is_player:
                color = UI_AMMO_BULLET if self.proj_type == 'bullet' else UI_AMMO_SHELL
            else:
                color = (200, 80, 60)
            pygame.draw.circle(surface, color,
                               (int(tsx), int(tsy)), trail_size)

        # Projectile body
        if self.is_player:
            if self.proj_type == 'bullet':
                color = UI_AMMO_BULLET
            else:
                color = UI_AMMO_SHELL
        else:
            color = (220, 80, 50)

        pygame.draw.circle(surface, color, (int(sx), int(sy)), self.size)

        # Glow
        glow_surf = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 50),
                           (self.size * 3, self.size * 3), self.size * 3)
        surface.blit(glow_surf,
                     (int(sx - self.size * 3), int(sy - self.size * 3)))


class ProjectileManager:
    """Manages all active projectiles."""

    def __init__(self):
        self.projectiles = []

    def spawn(self, x, y, angle, config, is_player=True):
        """Spawn projectile(s) based on weapon config."""
        count = config.get('count', 1)
        spread = config.get('spread', 0)
        damage = config.get('damage', 10)
        speed = config.get('speed', 15)
        size = config.get('size', 3)
        piercing = config.get('piercing', False)
        proj_type = config.get('type', 'bullet')

        if count == 1 and spread == 0:
            # Single shot
            self.projectiles.append(
                Projectile(x, y, angle, speed, damage, size,
                           is_player, piercing, proj_type)
            )
        else:
            # Spread shot
            spread_rad = math.radians(spread)
            start_angle = angle - spread_rad / 2
            for i in range(count):
                if count > 1:
                    a = start_angle + (spread_rad * i / (count - 1))
                else:
                    a = angle
                # Add slight random variation
                a += (hash(str(i) + str(self._tick())) % 100 - 50) * 0.003
                self.projectiles.append(
                    Projectile(x, y, a, speed + (hash(str(i)) % 4 - 2),
                               damage, size, is_player, piercing, proj_type)
                )

    def spawn_enemy_bullet(self, x, y, angle, speed=8, damage=10, size=4):
        """Spawn a single enemy projectile."""
        self.projectiles.append(
            Projectile(x, y, angle, speed, damage, size,
                       is_player=False, proj_type='enemy')
        )

    def _tick(self):
        import time
        return int(time.time() * 1000)

    def update(self, level_width, level_height):
        for p in self.projectiles:
            p.update()
            # Remove if out of bounds
            if (p.x < -50 or p.x > level_width + 50 or
                    p.y < -50 or p.y > level_height + 50):
                p.alive = False
        self.projectiles = [p for p in self.projectiles if p.alive]

    def draw(self, surface, camera):
        for p in self.projectiles:
            p.draw(surface, camera)

    def get_player_projectiles(self):
        return [p for p in self.projectiles if p.is_player]

    def get_enemy_projectiles(self):
        return [p for p in self.projectiles if not p.is_player]
