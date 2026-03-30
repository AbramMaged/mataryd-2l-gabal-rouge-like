"""
game_over.py — Game over screen with stats.
"""
import pygame
from art.colors import *


class GameOverScreen:
    """Game over screen with stats and retry/quit options."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.selected = 0
        self.options = ["RETRY", "MAIN MENU"]
        self.result = None
        self.stats = {}
        self.time = 0

    def set_stats(self, wave, kills, time_played):
        self.stats = {
            "Waves Survived": wave,
            "Enemies Killed": kills,
            "Time": f"{int(time_played // 60)}:{int(time_played % 60):02d}",
        }
        self.selected = 0
        self.result = None
        self.time = 0

    def handle_input(self, events):
        self.result = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        self.result = "retry"
                    else:
                        self.result = "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self._btn_rects()):
                    if rect.collidepoint(event.pos):
                        self.result = "retry" if i == 0 else "menu"

        mx, my = pygame.mouse.get_pos()
        for i, rect in enumerate(self._btn_rects()):
            if rect.collidepoint(mx, my):
                self.selected = i

    def _btn_rects(self):
        btn_w, btn_h = 200, 45
        start_y = self.screen_h // 2 + 80
        rects = []
        for i in range(len(self.options)):
            x = self.screen_w // 2 - btn_w // 2
            y = start_y + i * (btn_h + 15)
            rects.append(pygame.Rect(x, y, btn_w, btn_h))
        return rects

    def draw(self, surface):
        self.time += 1

        # Dark red-ish overlay
        overlay = pygame.Surface(
            (self.screen_w, self.screen_h), pygame.SRCALPHA
        )
        alpha = min(220, self.time * 5)
        overlay.fill((25, 10, 10, alpha))
        surface.blit(overlay, (0, 0))

        if self.time < 10:
            return  # Fade in delay

        # Title
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("GAME OVER", True, (200, 50, 50))
        title_rect = title.get_rect(
            centerx=self.screen_w // 2,
            centery=self.screen_h // 2 - 80
        )
        shadow = font_title.render("GAME OVER", True, (60, 15, 15))
        surface.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title, title_rect)

        # Stats
        font_stat = pygame.font.Font(None, 28)
        stat_y = self.screen_h // 2 - 10
        for key, val in self.stats.items():
            stat_text = font_stat.render(f"{key}: {val}", True, UI_TEXT)
            stat_rect = stat_text.get_rect(
                centerx=self.screen_w // 2, top=stat_y
            )
            surface.blit(stat_text, stat_rect)
            stat_y += 30

        # Buttons
        font_btn = pygame.font.Font(None, 30)
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
