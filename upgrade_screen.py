"""
upgrade_screen.py — Post-wave upgrade selection with 3 cards.
"""
import pygame
import math
from art.colors import *


class UpgradeScreen:
    """Displays 3 upgrade cards for player to choose from."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.upgrades = []
        self.selected = 0
        self.result = None  # Index of selected upgrade, or None
        self.time = 0
        self.appear_timer = 0

    def set_upgrades(self, upgrades):
        self.upgrades = upgrades
        self.selected = 0
        self.result = None
        self.time = 0
        self.appear_timer = 20

    def handle_input(self, events):
        if self.appear_timer > 0:
            return

        self.result = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected = (self.selected - 1) % len(self.upgrades)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected = (self.selected + 1) % len(self.upgrades)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.result = self.selected
                elif event.key == pygame.K_1:
                    self.selected = 0
                    self.result = 0
                elif event.key == pygame.K_2 and len(self.upgrades) > 1:
                    self.selected = 1
                    self.result = 1
                elif event.key == pygame.K_3 and len(self.upgrades) > 2:
                    self.selected = 2
                    self.result = 2
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(self._card_rects()):
                        if rect.collidepoint(event.pos):
                            self.result = i

        # Mouse hover
        mx, my = pygame.mouse.get_pos()
        for i, rect in enumerate(self._card_rects()):
            if rect.collidepoint(mx, my):
                self.selected = i

    def _card_rects(self):
        card_w, card_h = 200, 260
        spacing = 30
        total_w = len(self.upgrades) * card_w + (len(self.upgrades) - 1) * spacing
        start_x = self.screen_w // 2 - total_w // 2
        start_y = self.screen_h // 2 - card_h // 2

        rects = []
        for i in range(len(self.upgrades)):
            x = start_x + i * (card_w + spacing)
            rects.append(pygame.Rect(x, start_y, card_w, card_h))
        return rects

    def draw(self, surface):
        self.time += 1
        if self.appear_timer > 0:
            self.appear_timer -= 1

        # Dark overlay
        overlay = pygame.Surface(
            (self.screen_w, self.screen_h), pygame.SRCALPHA
        )
        overlay.fill((15, 10, 8, 200))
        surface.blit(overlay, (0, 0))

        # Title
        font_title = pygame.font.Font(None, 48)
        title = font_title.render("CHOOSE AN UPGRADE", True, MENU_TITLE)
        title_rect = title.get_rect(
            centerx=self.screen_w // 2,
            top=self.screen_h // 2 - 180
        )
        surface.blit(title, title_rect)

        # Cards
        font_name = pygame.font.Font(None, 26)
        font_desc = pygame.font.Font(None, 20)

        for i, (upgrade, rect) in enumerate(
                zip(self.upgrades, self._card_rects())):
            is_selected = (i == self.selected)

            # Appear animation
            if self.appear_timer > 0:
                progress = 1 - (self.appear_timer / 20.0)
                rect = pygame.Rect(
                    rect.x, rect.y + int(50 * (1 - progress)),
                    rect.w, rect.h
                )

            # Selected card lift
            if is_selected:
                rect = rect.move(0, -8)

            # Card background
            if is_selected:
                # Glow
                glow = pygame.Surface(
                    (rect.w + 20, rect.h + 20), pygame.SRCALPHA
                )
                pygame.draw.rect(glow, (218, 175, 65, 50),
                                 (0, 0, rect.w + 20, rect.h + 20),
                                 border_radius=12)
                surface.blit(glow, (rect.x - 10, rect.y - 10))

            pygame.draw.rect(surface, MENU_BG, rect, border_radius=10)
            border_color = MENU_TITLE if is_selected else MENU_BORDER
            pygame.draw.rect(surface, border_color, rect, 2,
                             border_radius=10)

            # Icon area
            icon_rect = pygame.Rect(
                rect.x + 20, rect.y + 20, rect.w - 40, 80
            )
            icon_color = self._get_icon_color(upgrade.get("icon", ""))
            pygame.draw.rect(surface, icon_color, icon_rect,
                             border_radius=6)
            self._draw_icon(surface, icon_rect, upgrade.get("icon", ""))

            # Name
            name = font_name.render(upgrade["name"], True,
                                    MENU_TITLE if is_selected else UI_TEXT)
            name_rect = name.get_rect(
                centerx=rect.centerx, top=icon_rect.bottom + 15
            )
            surface.blit(name, name_rect)

            # Description — word wrap
            desc_y = name_rect.bottom + 10
            words = upgrade["description"].split()
            lines = []
            current_line = ""
            for word in words:
                test = current_line + " " + word if current_line else word
                if font_desc.size(test)[0] < rect.w - 30:
                    current_line = test
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            for line in lines:
                desc_surf = font_desc.render(line, True, (180, 170, 150))
                desc_rect = desc_surf.get_rect(
                    centerx=rect.centerx, top=desc_y
                )
                surface.blit(desc_surf, desc_rect)
                desc_y += 18

            # Key hint
            key_text = font_desc.render(f"[{i + 1}]", True,
                                        MENU_TITLE if is_selected else (100, 90, 70))
            key_rect = key_text.get_rect(
                centerx=rect.centerx, bottom=rect.bottom - 10
            )
            surface.blit(key_text, key_rect)

        # Footer
        font_hint = pygame.font.Font(None, 20)
        hint = font_hint.render(
            "←→ / Mouse to Select  |  Enter / Click to confirm  |  1/2/3 Quick select",
            True, (100, 90, 70)
        )
        hint_rect = hint.get_rect(
            centerx=self.screen_w // 2,
            top=self._card_rects()[0].bottom + 30
        )
        surface.blit(hint, hint_rect)

    def _get_icon_color(self, icon_type):
        colors = {
            "stamina": (40, 80, 50),
            "shield": (50, 60, 80),
            "shotgun": (80, 35, 30),
            "deagle": (70, 60, 30),
            "heart": (80, 30, 30),
            "speed": (30, 60, 80),
        }
        return colors.get(icon_type, (50, 50, 50))

    def _draw_icon(self, surface, rect, icon_type):
        """Draw an icon representing the upgrade type."""
        cx, cy = rect.centerx, rect.centery
        if icon_type == "heart":
            # Heart
            s = 15
            pygame.draw.circle(surface, UI_RED, (cx - 6, cy - 4), s // 2)
            pygame.draw.circle(surface, UI_RED, (cx + 6, cy - 4), s // 2)
            pygame.draw.polygon(surface, UI_RED, [
                (cx - 12, cy - 2), (cx + 12, cy - 2), (cx, cy + 12)
            ])
        elif icon_type == "stamina":
            # Lightning bolt
            points = [
                (cx - 3, cy - 15), (cx + 8, cy - 3),
                (cx + 1, cy - 3), (cx + 5, cy + 15),
                (cx - 6, cy + 3), (cx + 1, cy + 3),
            ]
            pygame.draw.polygon(surface, UI_STAMINA, points)
        elif icon_type == "shotgun":
            pygame.draw.rect(surface, (150, 150, 155),
                             (cx - 20, cy - 2, 40, 5))
            pygame.draw.rect(surface, WOOD, (cx - 8, cy + 2, 12, 5))
        elif icon_type == "deagle":
            pygame.draw.rect(surface, (120, 120, 130),
                             (cx - 12, cy - 3, 24, 6))
            pygame.draw.rect(surface, WOOD_DARK, (cx - 4, cy + 2, 6, 10))
        elif icon_type == "shield":
            pygame.draw.circle(surface, (100, 140, 200), (cx, cy), 16, 3)
            pygame.draw.circle(surface, (140, 180, 240), (cx, cy), 10, 2)
        elif icon_type == "speed":
            for i in range(3):
                offset = i * 8
                pygame.draw.line(surface, (80, 160, 220),
                                 (cx - 15 + offset, cy + 5),
                                 (cx - 5 + offset, cy - 8), 2)
