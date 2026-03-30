"""
Egyptian Farmer — Roguelike
A fast-paced 2D wave-based shooter.

Entry point: Run this file to start the game.
    python main.py
"""
import sys
import os

# Add game directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FULLSCREEN
from core.game import Game


def main():
    pygame.init()
    pygame.font.init()

    # Create window
    flags = 0
    if FULLSCREEN:
        flags = pygame.FULLSCREEN

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), flags
    )
    pygame.display.set_caption(TITLE)

    # Hide system cursor and use crosshair
    pygame.mouse.set_visible(True)

    # Run game
    game = Game(screen)
    game.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
