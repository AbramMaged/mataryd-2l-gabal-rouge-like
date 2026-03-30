"""
backgrounds.py — Parallax background layers for Egyptian countryside.
"""
import pygame
import math
import random
from art.colors import *


class Background:
    """Multi-layer parallax Egyptian countryside background."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Pre-generate random elements (use fixed seed for consistency)
        rng = random.Random(12345)
        self._stars = [(rng.randint(0, screen_w),
                        rng.randint(0, screen_h // 3),
                        rng.uniform(0.5, 2.0))
                       for _ in range(80)]
        self._palm_positions = [
            (rng.randint(0, screen_w), rng.uniform(0.7, 0.9))
            for _ in range(12)
        ]
        self._building_positions = [
            (rng.randint(0, screen_w),
             rng.randint(30, 55),
             rng.randint(25, 40))
            for _ in range(6)
        ]
        self._crop_x_offsets = [
            rng.randint(0, screen_w)
            for _ in range(25)
        ]
        self.time = 0

    def draw(self, surface, camera_x, wave_number=1):
        """Draw all background layers."""
        self.time += 1
        night_factor = min(1.0, max(0.0, (wave_number - 15) / 10.0))

        # Layer 0: Sky gradient (fills ENTIRE screen)
        self._draw_sky(surface, night_factor)

        # Layer 1: Distant pyramids (slowest parallax)
        self._draw_far_bg(surface, camera_x * 0.1, night_factor)

        # Layer 2: Mid buildings and palms
        self._draw_mid_bg(surface, camera_x * 0.3, night_factor)

        # Layer 3: Near ground fill
        self._draw_near_bg(surface, camera_x * 0.5, night_factor)

    def _draw_sky(self, surface, night):
        """Gradient sky — fills the ENTIRE screen."""
        top = self._lerp_color(SKY_TOP, SKY_NIGHT_TOP, night)
        mid = self._lerp_color(SKY_BOTTOM, SKY_NIGHT_BOTTOM, night)
        bottom = self._lerp_color(SAND, (40, 30, 25), night)

        h = self.screen_h
        # Top half: sky gradient
        for y in range(h * 2 // 3):
            t = y / (h * 2 // 3)
            r = int(top[0] + (mid[0] - top[0]) * t)
            g = int(top[1] + (mid[1] - top[1]) * t)
            b = int(top[2] + (mid[2] - top[2]) * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_w, y))

        # Bottom third: horizon to ground
        start_y = h * 2 // 3
        for y in range(start_y, h):
            t = (y - start_y) / max(1, h - start_y)
            r = int(mid[0] + (bottom[0] - mid[0]) * t)
            g = int(mid[1] + (bottom[1] - mid[1]) * t)
            b = int(mid[2] + (bottom[2] - mid[2]) * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_w, y))

        # Stars at night
        if night > 0.2:
            for sx, sy, brightness in self._stars:
                twinkle = abs(math.sin(self.time * 0.02 * brightness + sx))
                if twinkle > 0.3:
                    size = 1 if brightness < 1.2 else 2
                    c = min(255, int(200 * twinkle * night))
                    pygame.draw.circle(surface, (c, c, int(c * 0.9)),
                                       (sx, sy), size)

    def _draw_far_bg(self, surface, offset, night):
        """Distant pyramid silhouettes and dune horizon line."""
        base_y = int(self.screen_h * 0.5)

        # Pyramids silhouette
        pyramid_color = self._lerp_color(SAND_DARK, (40, 30, 50), night)
        pyramid_positions = [200, 600, 1050]
        for i, px in enumerate(pyramid_positions):
            x = int(px - offset) % self.screen_w
            size = 55 + i * 15
            points = [
                (x, base_y + 10),
                (x + size, base_y + 10),
                (x + size // 2, base_y - size + 15),
            ]
            pygame.draw.polygon(surface, pyramid_color, points)

        # Simple dune horizon — smooth sine wave
        dune_color = self._lerp_color(SAND, (50, 40, 60), night)
        dune_points = [(0, self.screen_h)]
        for x in range(0, self.screen_w + 20, 8):
            wave1 = math.sin((x + offset * 0.5) * 0.008) * 25
            wave2 = math.sin((x + offset * 0.3) * 0.015) * 12
            y = base_y + 20 + wave1 + wave2
            dune_points.append((x, int(y)))
        dune_points.append((self.screen_w, self.screen_h))
        pygame.draw.polygon(surface, dune_color, dune_points)

    def _draw_mid_bg(self, surface, offset, night):
        """Mid-ground: mud brick buildings and palm trees."""
        base_y = int(self.screen_h * 0.62)

        # Ground fill from mid to bottom
        mid_ground = self._lerp_color(SAND_DARK, (45, 35, 28), night)
        pygame.draw.rect(surface, mid_ground,
                         (0, base_y, self.screen_w, self.screen_h - base_y))

        # Buildings
        bldg_color = self._lerp_color(MUD_BRICK, (60, 45, 35), night)
        bldg_dark = self._lerp_color(MUD_BRICK_DARK, (40, 30, 25), night)
        for bx, bw, bh in self._building_positions:
            x = int(bx - offset * 0.6) % self.screen_w
            rect = pygame.Rect(x, base_y - bh, bw, bh)
            pygame.draw.rect(surface, bldg_color, rect)
            pygame.draw.rect(surface, bldg_dark, rect, 2)
            # Door
            pygame.draw.rect(surface, WOOD_DARK,
                             (x + bw // 2 - 4, base_y - 14, 8, 14))

        # Palm trees
        trunk_color = self._lerp_color(PALM_TRUNK, (50, 35, 20), night)
        leaf_color = self._lerp_color(PALM_GREEN, (25, 50, 25), night)
        for px, scale in self._palm_positions:
            x = int(px - offset * 0.8) % self.screen_w
            trunk_h = int(55 * scale)
            trunk_top = base_y - trunk_h
            # Trunk
            pygame.draw.line(surface, trunk_color,
                             (x, base_y), (x + 2, trunk_top), 4)
            # Leaves
            for angle_i in range(-3, 4):
                lx = x + 2 + int(math.cos(angle_i * 0.6) * 22)
                ly = trunk_top + int(math.sin(angle_i * 0.6) * 8) - 5
                sway = int(math.sin(self.time * 0.03 + px * 0.1) * 2)
                pygame.draw.line(surface, leaf_color,
                                 (x + 2, trunk_top),
                                 (lx + sway, ly), 2)

    def _draw_near_bg(self, surface, offset, night):
        """Near ground: sandy terrain with crops."""
        base_y = int(self.screen_h * 0.78)
        ground_color = self._lerp_color(SAND, (60, 50, 40), night)

        # Ground fill
        pygame.draw.rect(surface, ground_color,
                         (0, base_y, self.screen_w, self.screen_h - base_y))

        # Crop rows
        crop_color = self._lerp_color(CROP_GREEN, (30, 55, 20), night)
        for cx in self._crop_x_offsets:
            x = int(cx - offset * 0.4) % self.screen_w
            sway = int(math.sin(self.time * 0.04 + cx * 0.1) * 2)
            height = 10 + int(abs(math.sin(cx * 0.3)) * 8)
            pygame.draw.line(surface, crop_color,
                             (x, base_y - 2),
                             (x + sway, base_y - height), 2)

    def _lerp_color(self, c1, c2, t):
        """Linearly interpolate between two colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )
