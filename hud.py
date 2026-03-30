"""
hud.py — In-game HUD: poker heart cards, ammo display, stamina bars, wave counter.
"""
import pygame
import math
from art.colors import *


class HUD:
    """In-game heads-up display."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

    def draw(self, surface, player, wave_number, weapon_type, combo_count=0, combo_timer=0):
        """Draw all HUD elements."""
        self._draw_hearts(surface, player)
        self._draw_stamina(surface, player)
        self._draw_ammo(surface, player, weapon_type)
        self._draw_wave_counter(surface, wave_number)
        self._draw_weapon_indicator(surface, weapon_type)
        
        if combo_count > 0:
            self._draw_combo_counter(surface, combo_count, combo_timer)

        # Reload indicator
        if player.current_weapon.is_reloading:
            self._draw_reload_bar(surface, player)

    def _draw_combo_counter(self, surface, combo_count, combo_timer):
        """Draw exciting combo counter multiplier."""
        # Scale and shake based on combo
        scale = min(1.5, 1.0 + (combo_count * 0.05))
        bounce = math.sin(pygame.time.get_ticks() * 0.01) * min(5, combo_count)
        
        font_size = int(32 * scale)
        font = pygame.font.Font(None, font_size)
        
        # Color shift
        color = (255, 200, 50)
        if combo_count > 10:
            color = (255, 100, 50)
        if combo_count > 25:
            color = (255, 50, 50)
            
        text = font.render(f"{combo_count}x COMBO!", True, color)
        # Position near top right
        x = self.screen_w - 200
        y = 60 + int(bounce)
        
        rect = text.get_rect(center=(x, y))
        
        # Shadow
        shadow = font.render(f"{combo_count}x COMBO!", True, (20, 20, 20))
        surface.blit(shadow, (rect.x + 2, rect.y + 2))
        surface.blit(text, rect)
        
        # Timer bar
        bar_w = 100
        bar_h = 4
        progress = combo_timer / 300.0  # Assumes 300 max timer
        pygame.draw.rect(surface, (40, 40, 40), (x - bar_w//2, y + 25, bar_w, bar_h))
        pygame.draw.rect(surface, color, (x - bar_w//2, y + 25, int(bar_w * progress), bar_h))

    def _draw_hearts(self, surface, player):
        """Draw poker heart cards for health."""
        card_w, card_h = 32, 44
        spacing = 6
        start_x = 20
        start_y = self.screen_h - 70

        for i in range(player.max_hearts):
            x = start_x + i * (card_w + spacing)
            y = start_y
            is_alive = i < player.hearts
            flip_timer = 0
            if i < len(player.heart_flip_timers):
                flip_timer = player.heart_flip_timers[i]

            self._draw_heart_card(surface, x, y, card_w, card_h,
                                  is_alive, flip_timer)

    def _draw_heart_card(self, surface, x, y, w, h, is_alive, flip_timer):
        """Draw a single poker heart card."""
        # Flip animation — squish horizontally
        if flip_timer > 0:
            progress = flip_timer / 20.0
            scale = abs(math.cos(progress * math.pi))
            actual_w = max(2, int(w * scale))
            x = x + (w - actual_w) // 2
            w = actual_w

        # Card background
        if is_alive:
            # Face up — white card with red heart
            card_rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(surface, UI_CARD_WHITE, card_rect,
                             border_radius=4)
            pygame.draw.rect(surface, UI_CARD_BORDER, card_rect, 2,
                             border_radius=4)

            # Heart symbol
            if w > 10:  # Only draw if card is wide enough (during flip)
                hx = x + w // 2
                hy = y + h // 2
                heart_size = min(w // 3, 10)
                self._draw_heart_symbol(surface, hx, hy, heart_size, UI_RED)

                # Corner marks
                if w > 20:
                    font = pygame.font.Font(None, 16)
                    text = font.render("♥", True, UI_RED)
                    surface.blit(text, (x + 3, y + 2))
        else:
            # Face down — card back (red pattern)
            card_rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(surface, UI_CARD_BACK, card_rect,
                             border_radius=4)
            pygame.draw.rect(surface, UI_RED_DARK, card_rect, 2,
                             border_radius=4)

            # Cross-hatch pattern on back
            if w > 10:
                inner = pygame.Rect(x + 4, y + 4, w - 8, h - 8)
                pygame.draw.rect(surface, UI_RED_DARK, inner, 1,
                                 border_radius=2)

    def _draw_heart_symbol(self, surface, cx, cy, size, color):
        """Draw a heart shape."""
        s = size
        # Two circles for top of heart
        pygame.draw.circle(surface, color, (cx - s // 2, cy - s // 3), s // 2)
        pygame.draw.circle(surface, color, (cx + s // 2, cy - s // 3), s // 2)
        # Triangle for bottom
        points = [
            (cx - s, cy - s // 4),
            (cx + s, cy - s // 4),
            (cx, cy + s),
        ]
        pygame.draw.polygon(surface, color, points)

    def _draw_stamina(self, surface, player):
        """Draw stamina bars."""
        bar_w = 24
        bar_h = 8
        spacing = 4
        start_x = 20
        start_y = self.screen_h - 100

        # Label
        font = pygame.font.Font(None, 18)
        label = font.render("STAMINA", True, UI_TEXT)
        surface.blit(label, (start_x, start_y - 14))

        for i in range(player.max_stamina):
            x = start_x + i * (bar_w + spacing)
            y = start_y
            rect = pygame.Rect(x, y, bar_w, bar_h)

            if i < player.stamina:
                # Full
                pygame.draw.rect(surface, UI_STAMINA, rect, border_radius=2)
                # Glow
                glow_rect = pygame.Rect(x + 2, y + 1, bar_w - 4, bar_h // 2)
                pygame.draw.rect(surface, (130, 220, 170), glow_rect,
                                 border_radius=1)
            else:
                # Empty
                pygame.draw.rect(surface, UI_STAMINA_EMPTY, rect,
                                 border_radius=2)

            pygame.draw.rect(surface, (40, 60, 40), rect, 1, border_radius=2)

    def _draw_ammo(self, surface, player, weapon_type):
        """Draw ammo as shotgun shells or bullets."""
        start_x = 20
        start_y = self.screen_h - 150

        weapon = player.current_weapon
        max_ammo = weapon.get_max_ammo()
        current = weapon.current_ammo

        # Weapon name
        font = pygame.font.Font(None, 22)
        name_text = font.render(weapon.name.upper(), True, UI_GOLD)
        surface.blit(name_text, (start_x, start_y - 20))

        if weapon_type == "shotgun":
            self._draw_shells(surface, start_x, start_y,
                              current, max_ammo)
        else:
            self._draw_bullets(surface, start_x, start_y,
                               current, max_ammo)

    def _draw_shells(self, surface, start_x, start_y, current, max_ammo):
        """Draw pixel-art Enter the Gungeon style shotgun shells."""
        shell_w = 12
        shell_h = 24
        spacing = 6

        for i in range(max_ammo):
            x = start_x + i * (shell_w + spacing)
            y = start_y

            if i < current:
                # Gungeon-style bullet: black outline, red body, gold base
                # Outline
                pygame.draw.rect(surface, (20, 20, 20), (x-1, y-1, shell_w+2, shell_h+2))
                # Brass base
                pygame.draw.rect(surface, (200, 160, 40), (x, y + shell_h - 6, shell_w, 6))
                pygame.draw.rect(surface, (140, 100, 20), (x, y + shell_h - 6, shell_w, 6), 1)
                pygame.draw.rect(surface, (200, 160, 40), (x-2, y + shell_h - 2, shell_w+4, 2)) # Rim
                # Red body
                pygame.draw.rect(surface, (210, 40, 40), (x, y, shell_w, shell_h - 6))
                # Highlight
                pygame.draw.line(surface, (240, 100, 100), (x + 2, y + 2), (x + 2, y + shell_h - 8), 2)
                # Shadow
                pygame.draw.line(surface, (140, 20, 20), (x + shell_w - 2, y + 2), (x + shell_w - 2, y + shell_h - 8), 2)
            else:
                # Empty slot outline
                pygame.draw.rect(surface, (50, 40, 40), (x, y, shell_w, shell_h), 1)
                pygame.draw.rect(surface, (30, 20, 20), (x+1, y+1, shell_w-2, shell_h-2))

    def _draw_bullets(self, surface, start_x, start_y, current, max_ammo):
        """Draw pixel-art Enter the Gungeon style bullets."""
        bullet_w = 10
        bullet_h = 20
        spacing = 4

        for i in range(max_ammo):
            x = start_x + i * (bullet_w + spacing)
            y = start_y + 4

            if i < current:
                # Outline
                pygame.draw.rect(surface, (15, 15, 15), (x-1, y-1, bullet_w+2, bullet_h+2))
                
                # Brass casing
                pygame.draw.rect(surface, (190, 160, 60), (x, y + 6, bullet_w, bullet_h - 6))
                # Shadow/Highlight
                pygame.draw.line(surface, (240, 220, 120), (x+2, y+7), (x+2, y+bullet_h-2))
                pygame.draw.line(surface, (120, 90, 30), (x+bullet_w-2, y+7), (x+bullet_w-2, y+bullet_h-2))
                
                # Bullet tip (copper)
                pygame.draw.rect(surface, (160, 100, 40), (x, y+2, bullet_w, 4))
                pygame.draw.rect(surface, (160, 100, 40), (x+2, y, bullet_w-4, 2))
                pygame.draw.rect(surface, (15, 15, 15), (x, y, bullet_w, 2), 1)
            else:
                # Empty slot
                pygame.draw.rect(surface, (40, 35, 30), (x, y, bullet_w, bullet_h), 1)
                pygame.draw.rect(surface, (25, 20, 15), (x+1, y+1, bullet_w-2, bullet_h-2))

    def _draw_wave_counter(self, surface, wave_number):
        """Draw wave number."""
        font_large = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 20)

        # Wave text
        wave_text = font_large.render(f"WAVE {wave_number}", True, UI_GOLD)
        wave_rect = wave_text.get_rect(
            centerx=self.screen_w // 2, top=15
        )
        # Shadow
        shadow = font_large.render(f"WAVE {wave_number}", True, UI_TEXT_SHADOW)
        surface.blit(shadow, (wave_rect.x + 2, wave_rect.y + 2))
        surface.blit(wave_text, wave_rect)

    def _draw_weapon_indicator(self, surface, weapon_type):
        """Draw current weapon indicator in bottom right."""
        font = pygame.font.Font(None, 18)
        x = self.screen_w - 80
        y = self.screen_h - 70

        # Active weapon highlight
        weapons = [("1", "deagle"), ("2", "shotgun")]
        for i, (key, wtype) in enumerate(weapons):
            wy = y + i * 18
            if wtype == weapon_type:
                color = UI_GOLD
                prefix = "▶ "
            else:
                color = (120, 110, 90)
                prefix = "  "
            text = font.render(f"{prefix}[{key}] {wtype.upper()}", True, color)
            surface.blit(text, (x, wy))

    def _draw_reload_bar(self, surface, player):
        """Draw reload progress bar near player."""
        weapon = player.current_weapon
        if weapon.reload_timer <= 0:
            return

        progress = 1 - (weapon.reload_timer /
                         max(1, int(weapon.reload_time / weapon.reload_speed_mult)))
        bar_w = 50
        bar_h = 6
        bx = self.screen_w // 2 - bar_w // 2
        by = self.screen_h - 80

        pygame.draw.rect(surface, (40, 40, 40), (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, UI_GOLD,
                         (bx, by, int(bar_w * progress), bar_h))

        font = pygame.font.Font(None, 16)
        text = font.render("RELOADING", True, UI_GOLD)
        text_rect = text.get_rect(centerx=bx + bar_w // 2, bottom=by - 2)
        surface.blit(text, text_rect)
