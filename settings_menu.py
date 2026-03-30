"""
settings_menu.py — Settings screen for audio, display, and controls.
"""
import pygame
from art.colors import *
from core import settings


class SettingsMenu:
    """Settings screen: audio volumes, display, controls."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.selected = 0
        self.result = None  # None or "back"
        self.waiting_for_key = None # Holds the name of the action waiting for a key press

        # Keybind options generator
        def make_keybind_opt(action, name):
            return {
                "name": name,
                "type": "keybind",
                "action": action
            }

        self.options = [
            {"name": "Master Volume", "type": "slider",
             "get": lambda: settings.MASTER_VOLUME,
             "set": lambda v: setattr(settings, 'MASTER_VOLUME', v)},
            {"name": "SFX Volume", "type": "slider",
             "get": lambda: settings.SFX_VOLUME,
             "set": lambda v: setattr(settings, 'SFX_VOLUME', v)},
            {"name": "Screen Shake", "type": "slider",
             "get": lambda: settings.SCREEN_SHAKE_INTENSITY,
             "set": lambda v: setattr(settings, 'SCREEN_SHAKE_INTENSITY', v)},
            {"name": "Fullscreen", "type": "toggle",
             "get": lambda: settings.FULLSCREEN,
             "set": self._toggle_fullscreen},
            make_keybind_opt("jump", "Jump Key"),
            make_keybind_opt("dash", "Dash Key"),
            make_keybind_opt("parry", "Parry Key"),
            {"name": "Back", "type": "action"},
        ]

    def _toggle_fullscreen(self, value):
        settings.FULLSCREEN = value
        flags = pygame.FULLSCREEN if value else 0
        pygame.display.set_mode((self.screen_w, self.screen_h), flags)

    def handle_input(self, events, input_handler):
        self.result = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.waiting_for_key:
                    # Cancel on ESC, otherwise bind the key
                    if event.key != pygame.K_ESCAPE:
                        settings.KEYBINDS[self.waiting_for_key] = event.key
                    self.waiting_for_key = None
                    return

                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_ESCAPE:
                    self.result = "back"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    opt = self.options[self.selected]
                    if opt["type"] == "action":
                        self.result = "back"
                    elif opt["type"] == "toggle":
                        opt["set"](not opt["get"]())
                    elif opt["type"] == "keybind":
                        self.waiting_for_key = opt["action"]
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self._adjust_slider(-0.1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self._adjust_slider(0.1)

    def _adjust_slider(self, delta):
        opt = self.options[self.selected]
        if opt["type"] == "slider":
            val = max(0.0, min(1.0, opt["get"]() + delta))
            opt["set"](round(val, 1))

    def draw(self, surface):
        # Background overlay
        surface.fill(MENU_BG)

        # Title
        font_title = pygame.font.Font(None, 52)
        title = font_title.render("SETTINGS", True, MENU_TITLE)
        title_rect = title.get_rect(
            centerx=self.screen_w // 2, top=60
        )
        surface.blit(title, title_rect)

        # Decorative line
        pygame.draw.line(surface, MENU_BORDER,
                         (self.screen_w // 2 - 80, title_rect.bottom + 10),
                         (self.screen_w // 2 + 80, title_rect.bottom + 10), 2)

        # Options
        font_opt = pygame.font.Font(None, 30)
        start_y = 180
        for i, opt in enumerate(self.options):
            y = start_y + i * 60
            is_selected = (i == self.selected)
            color = MENU_TITLE if is_selected else UI_TEXT

            if opt["type"] == "slider":
                # Label
                label = font_opt.render(opt["name"], True, color)
                surface.blit(label, (self.screen_w // 2 - 180, y))

                # Slider bar
                bar_x = self.screen_w // 2 + 40
                bar_w = 200
                bar_h = 8
                val = opt["get"]()

                pygame.draw.rect(surface, (50, 40, 30),
                                 (bar_x, y + 8, bar_w, bar_h),
                                 border_radius=4)
                pygame.draw.rect(surface, MENU_TITLE if is_selected else UI_GOLD_DARK,
                                 (bar_x, y + 8, int(bar_w * val), bar_h),
                                 border_radius=4)

                # Value text
                val_text = font_opt.render(f"{int(val * 100)}%", True, color)
                surface.blit(val_text, (bar_x + bar_w + 10, y))

                # Selector arrows
                if is_selected:
                    arrow_l = font_opt.render("◄", True, MENU_TITLE)
                    arrow_r = font_opt.render("►", True, MENU_TITLE)
                    surface.blit(arrow_l, (bar_x - 20, y + 3))
                    surface.blit(arrow_r, (bar_x + bar_w + 60, y + 3))

            elif opt["type"] == "toggle":
                label = font_opt.render(opt["name"], True, color)
                surface.blit(label, (self.screen_w // 2 - 180, y))

                val = opt["get"]()
                val_text = font_opt.render(
                    "ON" if val else "OFF", True,
                    UI_STAMINA if val else (120, 80, 60)
                )
                surface.blit(val_text, (self.screen_w // 2 + 80, y))

            elif opt["type"] == "keybind":
                label = font_opt.render(opt["name"], True, color)
                surface.blit(label, (self.screen_w // 2 - 180, y))

                action = opt["action"]
                current_key = settings.KEYBINDS.get(action, pygame.K_UNKNOWN)
                
                if self.waiting_for_key == action:
                    val_str = "PRESS ANY KEY..."
                    val_color = UI_STAMINA
                else:
                    val_str = pygame.key.name(current_key).upper()
                    val_color = (200, 200, 200)

                val_text = font_opt.render(val_str, True, val_color)
                surface.blit(val_text, (self.screen_w // 2 + 80, y))

            elif opt["type"] == "action":
                text = font_opt.render(opt["name"], True, color)
                text_rect = text.get_rect(
                    centerx=self.screen_w // 2, top=y
                )
                if is_selected:
                    btn_rect = text_rect.inflate(40, 10)
                    pygame.draw.rect(surface, MENU_BUTTON_HOVER, btn_rect,
                                     border_radius=6)
                    pygame.draw.rect(surface, MENU_TITLE, btn_rect, 2,
                                     border_radius=6)
                surface.blit(text, text_rect)

        # Footer hint
        font_hint = pygame.font.Font(None, 18)
        hint = font_hint.render(
            "↑↓ Navigate  |  ←→ Adjust  |  Enter: Select  |  ESC: Back",
            True, (100, 90, 70)
        )
        hint_rect = hint.get_rect(
            centerx=self.screen_w // 2,
            bottom=self.screen_h - 20
        )
        surface.blit(hint, hint_rect)
