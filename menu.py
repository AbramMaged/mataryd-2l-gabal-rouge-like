"""
menu.py — Main menu screen with Egyptian-themed styling.
"""
import pygame
import math
from art.colors import *
from art.backgrounds import Background


class MainMenu:
    """Main menu: START GAME, SETTINGS, QUIT."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.background = Background(screen_w, screen_h)
        self.selected = 0
        self.options = ["START GAME", "SETTINGS", "QUIT"]
        self.time = 0
        self.result = None  # "start", "settings", "quit"

    def handle_input(self, events, input_handler):
        self.result = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected == 0:
                        self.result = "start"
                    elif self.selected == 1:
                        self.result = "settings"
                    elif self.selected == 2:
                        self.result = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(self._button_rects()):
                        if rect.collidepoint(event.pos):
                            self.selected = i
                            if i == 0:
                                self.result = "start"
                            elif i == 1:
                                self.result = "settings"
                            elif i == 2:
                                self.result = "quit"

        # Mouse hover
        mx, my = pygame.mouse.get_pos()
        for i, rect in enumerate(self._button_rects()):
            if rect.collidepoint(mx, my):
                self.selected = i

    def _button_rects(self):
        rects = []
        btn_w, btn_h = 260, 50
        start_y = self.screen_h // 2 + 40
        for i in range(len(self.options)):
            x = self.screen_w // 2 - btn_w // 2
            y = start_y + i * (btn_h + 15)
            rects.append(pygame.Rect(x, y, btn_w, btn_h))
        return rects

    def draw(self, surface):
        self.time += 1

        # Background
        self.background.draw(surface, self.time * 0.3, wave_number=1)

        # Dark overlay
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((20, 15, 10, 140))
        surface.blit(overlay, (0, 0))

        # Title
        font_title = pygame.font.Font(None, 78)
        font_sub = pygame.font.Font(None, 28)

        title_text = "EGYPTIAN FARMER"
        title_surf = font_title.render(title_text, True, MENU_TITLE)
        title_rect = title_surf.get_rect(
            centerx=self.screen_w // 2,
            centery=self.screen_h // 2 - 60
        )
        # Title shadow
        shadow = font_title.render(title_text, True, (40, 25, 10))
        surface.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title_surf, title_rect)

        # Subtitle
        sub_text = "LAST STAND"
        pulse = abs(math.sin(self.time * 0.03)) * 0.3 + 0.7
        sub_color = (
            int(UI_TEXT[0] * pulse),
            int(UI_TEXT[1] * pulse),
            int(UI_TEXT[2] * pulse),
        )
        sub_surf = font_sub.render(sub_text, True, sub_color)
        sub_rect = sub_surf.get_rect(
            centerx=self.screen_w // 2,
            top=title_rect.bottom + 5
        )
        surface.blit(sub_surf, sub_rect)

        # Decorative line
        line_y = sub_rect.bottom + 15
        pygame.draw.line(surface, MENU_BORDER,
                         (self.screen_w // 2 - 100, line_y),
                         (self.screen_w // 2 + 100, line_y), 2)

        # Buttons
        font_btn = pygame.font.Font(None, 32)
        for i, (option, rect) in enumerate(
                zip(self.options, self._button_rects())):
            is_selected = (i == self.selected)

            if is_selected:
                # Highlighted button
                pygame.draw.rect(surface, MENU_BUTTON_HOVER, rect,
                                 border_radius=6)
                pygame.draw.rect(surface, MENU_TITLE, rect, 2,
                                 border_radius=6)
                text_color = MENU_TITLE
                # Glow effect
                glow = pygame.Surface(
                    (rect.w + 10, rect.h + 10), pygame.SRCALPHA
                )
                pygame.draw.rect(glow, (218, 175, 65, 30),
                                 (0, 0, rect.w + 10, rect.h + 10),
                                 border_radius=8)
                surface.blit(glow, (rect.x - 5, rect.y - 5))
            else:
                pygame.draw.rect(surface, MENU_BUTTON, rect,
                                 border_radius=6)
                pygame.draw.rect(surface, MENU_BORDER, rect, 1,
                                 border_radius=6)
                text_color = MENU_BUTTON_TEXT

            text = font_btn.render(option, True, text_color)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

        # Footer
        font_footer = pygame.font.Font(None, 18)
        controls = "WASD / Arrows: Move  |  Mouse: Aim & Shoot  |  Shift: Dash  |  Q: Switch Weapon"
        footer = font_footer.render(controls, True, (120, 110, 90))
        footer_rect = footer.get_rect(
            centerx=self.screen_w // 2,
            bottom=self.screen_h - 15
        )
        surface.blit(footer, footer_rect)
