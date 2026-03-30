"""
particles.py — Particle effects system.
Muzzle flash, blood, dust, shell casings, dash trails.
"""
import pygame
import random
import math
from art.colors import *
from core.settings import MAX_PARTICLES, PARTICLE_GRAVITY


class Particle:
    """Single particle with position, velocity, lifetime, and decay."""

    __slots__ = ['x', 'y', 'vel_x', 'vel_y', 'color', 'size',
                 'lifetime', 'max_lifetime', 'gravity', 'shrink']

    def __init__(self, x, y, vel_x, vel_y, color, size,
                 lifetime, gravity=True, shrink=True):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.shrink = shrink

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        if self.gravity:
            self.vel_y += PARTICLE_GRAVITY
        self.vel_x *= 0.98
        self.lifetime -= 1

    def draw(self, surface, camera):
        if self.lifetime <= 0:
            return
        sx, sy = camera.apply(self.x, self.y)
        progress = self.lifetime / self.max_lifetime
        if self.shrink:
            size = max(1, int(self.size * progress))
        else:
            size = self.size
        alpha = int(255 * progress)
        color = (*self.color[:3], min(255, alpha))

        # Draw with alpha
        if size <= 2:
            pygame.draw.circle(surface, self.color[:3],
                               (int(sx), int(sy)), size)
        else:
            ps = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, color, (size, size), size)
            surface.blit(ps, (int(sx - size), int(sy - size)))


class ParticleManager:
    """Manages all active particles."""

    def __init__(self):
        self.particles = []

    def emit_muzzle_flash(self, x, y, angle, count=8):
        """Muzzle flash effect at weapon barrel."""
        for _ in range(count):
            spread = random.uniform(-0.4, 0.4)
            speed = random.uniform(3, 8)
            a = angle + spread
            self.particles.append(Particle(
                x, y,
                math.cos(a) * speed, math.sin(a) * speed,
                random.choice([MUZZLE_FLASH, MUZZLE_FLASH_CORE,
                               (255, 200, 80)]),
                random.randint(2, 5),
                random.randint(4, 10),
                gravity=False, shrink=True
            ))

    def emit_blood(self, x, y, count=12):
        """Blood splatter on enemy hit."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 6)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed, math.sin(angle) * speed,
                random.choice([BLOOD, BLOOD_DARK, (150, 20, 20)]),
                random.randint(2, 4),
                random.randint(15, 30),
                gravity=True, shrink=True
            ))

    def emit_dust(self, x, y, count=6):
        """Dust cloud (landing, dashing)."""
        for _ in range(count):
            angle = random.uniform(-math.pi, 0)  # Upward
            speed = random.uniform(0.5, 3)
            self.particles.append(Particle(
                x + random.randint(-10, 10), y,
                math.cos(angle) * speed, math.sin(angle) * speed,
                random.choice([DUST, DUST_LIGHT, SAND_LIGHT]),
                random.randint(3, 6),
                random.randint(15, 25),
                gravity=False, shrink=True
            ))

    def emit_shell_casing(self, x, y, facing_right):
        """Ejected shell casing."""
        dir_x = -3 if facing_right else 3
        self.particles.append(Particle(
            x, y,
            dir_x + random.uniform(-1, 1),
            random.uniform(-4, -2),
            SHELL_CASING,
            3, 40,
            gravity=True, shrink=False
        ))

    def emit_dash_trail(self, x, y, w, h):
        """Dash motion trail."""
        for _ in range(3):
            self.particles.append(Particle(
                x + random.randint(0, w),
                y + random.randint(0, h),
                random.uniform(-1, 1),
                random.uniform(-0.5, 0.5),
                (200, 200, 255, 150),
                random.randint(4, 8),
                random.randint(6, 12),
                gravity=False, shrink=True
            ))

    def emit_death_explosion(self, x, y, count=20):
        """Explosion on enemy death."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed, math.sin(angle) * speed,
                random.choice([EXPLOSION, MUZZLE_FLASH,
                               (255, 100, 30), (200, 50, 20)]),
                random.randint(3, 7),
                random.randint(15, 30),
                gravity=True, shrink=True
            ))

    def emit_wall_slide(self, x, y):
        """Sparks/dust when wall sliding."""
        for _ in range(2):
            self.particles.append(Particle(
                x + random.randint(-3, 3), y + random.randint(-5, 5),
                random.uniform(-1, 1), random.uniform(0, 2),
                DUST,
                2, 10,
                gravity=True, shrink=True
            ))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles
                          if p.lifetime > 0]
        # Cap particles
        if len(self.particles) > MAX_PARTICLES:
            self.particles = self.particles[-MAX_PARTICLES:]

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)
