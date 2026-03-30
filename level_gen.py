"""
level_gen.py — Procedural level generation.
Creates platforms, walls, and ground for each wave.
"""
import pygame
import random
from art.colors import *
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Platform:
    """A platform the player and enemies can stand on."""

    def __init__(self, x, y, w, h, style="mud_brick"):
        self.rect = pygame.Rect(x, y, w, h)
        self.style = style

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.rect.x, self.rect.y)
        rect = pygame.Rect(int(sx), int(sy), self.rect.w, self.rect.h)

        if self.style == "mud_brick":
            pygame.draw.rect(surface, MUD_BRICK, rect)
            pygame.draw.rect(surface, MUD_BRICK_DARK, rect, 2)
            # Brick pattern
            for bx in range(0, self.rect.w, 20):
                for by in range(0, self.rect.h, 10):
                    offset = 10 if (by // 10) % 2 else 0
                    brect = pygame.Rect(
                        int(sx + bx + offset), int(sy + by), 18, 8
                    )
                    pygame.draw.rect(surface, MUD_BRICK_DARK, brect, 1)
        elif self.style == "wood":
            pygame.draw.rect(surface, WOOD, rect)
            pygame.draw.rect(surface, WOOD_DARK, rect, 2)
            # Wood grain lines
            for ly in range(0, self.rect.h, 6):
                pygame.draw.line(surface, WOOD_DARK,
                                 (int(sx), int(sy + ly)),
                                 (int(sx + self.rect.w), int(sy + ly)), 1)
        elif self.style == "hay":
            pygame.draw.rect(surface, HAY, rect)
            pygame.draw.rect(surface, HAY_DARK, rect, 2)
            # Hay texture
            for i in range(0, self.rect.w, 5):
                h_off = random.randint(-2, 2)
                pygame.draw.line(surface, HAY_DARK,
                                 (int(sx + i), int(sy)),
                                 (int(sx + i + h_off), int(sy + self.rect.h)), 1)


class Wall:
    """A vertical wall for wall-jumping."""

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.rect.x, self.rect.y)
        rect = pygame.Rect(int(sx), int(sy), self.rect.w, self.rect.h)
        pygame.draw.rect(surface, MUD_BRICK_DARK, rect)
        pygame.draw.rect(surface, DIRT_DARK, rect, 2)
        # Brick pattern
        for by in range(0, self.rect.h, 12):
            offset = 6 if (by // 12) % 2 else 0
            for bx in range(0, self.rect.w, 14):
                brect = pygame.Rect(
                    int(sx + bx + offset), int(sy + by), 12, 10
                )
                pygame.draw.rect(surface, DIRT, brect, 1)


class Level:
    """Generated level with platforms, walls, and ground."""

    def __init__(self, level_width, level_height, ground_y):
        self.width = level_width
        self.height = level_height
        self.ground_y = ground_y
        self.platforms = []
        self.walls = []

    def generate(self, wave_number=1):
        """Generate a new level layout."""
        self.platforms = []
        self.walls = []

        random.seed(wave_number * 42 + 7)  # Deterministic per wave

        # Side walls (for wall jumping)
        wall_thickness = 30
        self.walls.append(Wall(0, 0, wall_thickness, self.height))
        self.walls.append(Wall(self.width - wall_thickness, 0,
                               wall_thickness, self.height))

        # Generate platforms
        styles = ["mud_brick", "wood", "hay"]
        num_platforms = min(4 + wave_number // 2, 10)

        # Guaranteed middle platform
        mid_w = random.randint(120, 200)
        mid_x = self.width // 2 - mid_w // 2 + random.randint(-80, 80)
        mid_y = self.ground_y - random.randint(140, 200)
        self.platforms.append(
            Platform(mid_x, mid_y, mid_w, 18,
                     random.choice(styles))
        )

        # Additional platforms
        for i in range(num_platforms - 1):
            pw = random.randint(80, 180)
            px = random.randint(60, self.width - pw - 60)
            py = self.ground_y - random.randint(80, 340)
            style = random.choice(styles)

            # Make sure platforms don't overlap too much
            new_rect = pygame.Rect(px, py, pw, 18)
            overlap = False
            for plat in self.platforms:
                if new_rect.colliderect(plat.rect.inflate(40, 60)):
                    overlap = True
                    break
            if not overlap:
                self.platforms.append(Platform(px, py, pw, 18, style))

        # Parkour High Platform
        parkour_x = random.randint(150, self.width - 200)
        parkour_y = self.ground_y - random.randint(420, 480)
        self.platforms.append(Platform(parkour_x, parkour_y, 70, 18, "wood"))

        # Mid-height wall segments for wall jumping variety
        if wave_number >= 3:
            num_wall_cols = min(2, wave_number // 5 + 1)
            for _ in range(num_wall_cols):
                wx = random.choice([
                    random.randint(60, 120),
                    random.randint(self.width - 120, self.width - 60)
                ])
                wy = self.ground_y - random.randint(200, 350)
                wh = random.randint(100, 200)
                self.walls.append(Wall(wx, wy, 20, wh))

        random.seed()  # Reset random seed

    def draw(self, surface, camera):
        """Draw all level elements."""
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Ground
        gx, gy = camera.apply(0, self.ground_y)
        ground_h = screen_h - int(gy) + 50  # Extra to cover bottom
        if ground_h > 0:
            ground_rect = pygame.Rect(0, int(gy), screen_w, ground_h)
            pygame.draw.rect(surface, SAND_DARK, ground_rect)
            # Ground top line
            pygame.draw.line(surface, DIRT,
                             (0, int(gy)), (screen_w, int(gy)), 3)
            # Dirt layer
            pygame.draw.rect(surface, DIRT,
                             (0, int(gy) + 3, screen_w, 15))

        # Platforms
        for plat in self.platforms:
            plat.draw(surface, camera)

        # Walls
        for wall in self.walls:
            wall.draw(surface, camera)

    def get_spawn_points(self, count):
        """Get random spawn points for enemies."""
        points = []
        for _ in range(count):
            x = random.choice([
                random.randint(40, 150),
                random.randint(self.width - 150, self.width - 40)
            ])
            y = self.ground_y - 60
            points.append((x, y))
        return points
