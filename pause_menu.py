"""
pause_menu.py — Pause overlay with resume, settings, quit.
"""
import pygame
from art.colors import *


class PauseMenu:
    """Pause menu overlay."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.selected = 0
        self.options = ["RESUME", "SETTINGS", "QUIT TO MENU"]
        self.result = None  # "resume", "settings", "quit"

    def handle_input(self, events):
        self.result = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_ESCAPE:
                    self.result = "resume"
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    results = ["resume", "settings", "quit"]
                    self.result = results[self.selected]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self._btn_rects()):
                    if rect.collidepoint(event.pos):
                        results = ["resume", "settings", "quit"]
                        self.result = results[i]

        mx, my = pygame.mouse.get_pos()
        for i, rect in enumerate(self._btn_rects()):
            if rect.collidepoint(mx, my):
                self.selected = i

    def _btn_rects(self):
        btn_w, btn_h = 220, 45
        start_y = self.screen_h // 2 - 30
        rects = []
        for i in range(len(self.options)):
            x = self.screen_w // 2 - btn_w // 2
            y = start_y + i * (btn_h + 12)
            rects.append(pygame.Rect(x, y, btn_w, btn_h))
        return rects

    def draw(self, surface):
        # Dim overlay
        overlay = pygame.Surface(
            (self.screen_w, self.screen_h), pygame.SRCALPHA
        )
        overlay.fill((15, 12, 8, 180))
        surface.blit(overlay, (0, 0))

        # Title
        font_title = pygame.font.Font(None, 52)
        title = font_title.render("PAUSED", True, MENU_TITLE)
        title_rect = title.get_rect(
            centerx=self.screen_w // 2,
            centery=self.screen_h // 2 - 100
        )
        surface.blit(title, title_rect)

        # Buttons
        font_btn = pygame.font.Font(None, 28)
        for i, (opt, rect) in enumerate(
                zip(self.options, self._btn_rects())):
            is_selected = (i == self.selected)
            if is_selected:
                pygame.draw.rect(surface, MENU_BUTTON_HOVER, rect,
                                 border_radius=6)
                pygame.draw.rect(surface, MENU_TITLE, rect, 2,
                                 border_radius=6)
                color = MENU_TITLE
            else:
                pygame.draw.rect(surface, MENU_BUTTON, rect,
                                 border_radius=6)
                pygame.draw.rect(surface, MENU_BORDER, rect, 1,
                                 border_radius=6)
                color = UI_TEXT

            text = font_btn.render(opt, True, color)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
