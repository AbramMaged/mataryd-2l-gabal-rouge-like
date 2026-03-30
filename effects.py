"""
effects.py — Visual effects: screen flash, hit flash, slow-mo, damage indicators.
"""
import pygame


class EffectsManager:
    """Manages visual effects overlays."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Hit flash (red overlay)
        self.hit_flash_timer = 0
        self.hit_flash_duration = 6
        self.hit_flash_color = (255, 0, 0)

        # White flash (for kills, boss phase change)
        self.white_flash_timer = 0
        self.white_flash_duration = 4

        # Slow motion
        self.slow_mo_timer = 0
        self.slow_mo_factor = 0.3  # time scale during slow-mo

        # Damage numbers
        self.damage_numbers = []

        # Boss warning
        self.boss_warning_timer = 0
        self.boss_warning_text = ""

    def trigger_hit_flash(self):
        self.hit_flash_timer = self.hit_flash_duration

    def trigger_white_flash(self, duration=8):
        self.white_flash_timer = duration
        self.white_flash_duration = duration

    def trigger_slow_mo(self, duration=30):
        self.slow_mo_timer = duration

    def trigger_boss_warning(self, wave_num):
        self.boss_warning_timer = 120  # 2 seconds
        self.boss_warning_text = f"BOSS WAVE {wave_num}"

    def add_damage_number(self, x, y, damage, color=(255, 255, 255)):
        self.damage_numbers.append({
            'x': x, 'y': y,
            'damage': damage,
            'color': color,
            'timer': 40,
            'vel_y': -2
        })

    def get_time_scale(self):
        if self.slow_mo_timer > 0:
            return self.slow_mo_factor
        return 1.0

    def update(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.white_flash_timer > 0:
            self.white_flash_timer -= 1
        if self.slow_mo_timer > 0:
            self.slow_mo_timer -= 1
        if self.boss_warning_timer > 0:
            self.boss_warning_timer -= 1

        # Update damage numbers
        for dn in self.damage_numbers:
            dn['timer'] -= 1
            dn['y'] += dn['vel_y']
            dn['vel_y'] *= 0.95
        self.damage_numbers = [d for d in self.damage_numbers if d['timer'] > 0]

    def draw(self, surface, camera=None):
        """Draw all active effects as overlays."""
        # Hit flash
        if self.hit_flash_timer > 0:
            alpha = int(100 * (self.hit_flash_timer / self.hit_flash_duration))
            overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            overlay.fill((*self.hit_flash_color, alpha))
            surface.blit(overlay, (0, 0))

        # White flash
        if self.white_flash_timer > 0:
            alpha = int(180 * (self.white_flash_timer / max(self.white_flash_duration, 1)))
            overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, alpha))
            surface.blit(overlay, (0, 0))

        # Damage numbers
        font = pygame.font.Font(None, 24)
        for dn in self.damage_numbers:
            alpha = min(255, int(255 * (dn['timer'] / 40)))
            dx, dy = dn['x'], dn['y']
            if camera:
                dx, dy = camera.apply(dx, dy)
            text = font.render(str(int(dn['damage'])), True, dn['color'])
            text.set_alpha(alpha)
            surface.blit(text, (int(dx), int(dy)))

        # Boss warning
        if self.boss_warning_timer > 0:
            self._draw_boss_warning(surface)

    def _draw_boss_warning(self, surface):
        """Draw dramatic boss incoming warning."""
        # Pulsing overlay
        pulse = abs((self.boss_warning_timer % 20) - 10) / 10
        alpha = int(40 + pulse * 60)
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((150, 30, 30, alpha))
        surface.blit(overlay, (0, 0))

        # Warning text
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)

        text = font_large.render(self.boss_warning_text, True, (255, 80, 80))
        text_rect = text.get_rect(center=(self.screen_w // 2, self.screen_h // 2 - 20))
        # Shadow
        shadow = font_large.render(self.boss_warning_text, True, (40, 10, 10))
        surface.blit(shadow, (text_rect.x + 3, text_rect.y + 3))
        surface.blit(text, text_rect)

        sub = font_small.render("PREPARE YOURSELF", True, (200, 150, 50))
        sub_rect = sub.get_rect(center=(self.screen_w // 2, self.screen_h // 2 + 25))
        surface.blit(sub, sub_rect)
