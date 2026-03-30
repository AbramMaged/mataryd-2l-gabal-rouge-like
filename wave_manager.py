"""
wave_manager.py — Controls enemy spawning, wave progression, and difficulty scaling.
"""
import random
from core.settings import (
    BOSS_WAVE_INTERVAL, WAVE_ENEMY_BASE_COUNT,
    WAVE_ENEMY_SCALE, WAVE_STAT_SCALE
)
from entities.enemies.grunt import Grunt
from entities.enemies.runner import Runner
from entities.enemies.heavy import Heavy
from entities.enemies.boss import Boss


class WaveManager:
    """Manages wave progression, enemy spawning, and difficulty."""

    def __init__(self):
        self.wave_number = 0
        self.enemies = []
        self.wave_active = False
        self.wave_complete = False
        self.boss_wave = False
        self.between_waves = True
        self.between_wave_timer = 0
        self.boss_number = 0

    def start_wave(self, level):
        """Start the next wave."""
        self.wave_number += 1
        self.wave_active = True
        self.wave_complete = False
        self.between_waves = False
        self.boss_wave = (self.wave_number % BOSS_WAVE_INTERVAL == 0)

        if self.boss_wave:
            self.boss_number += 1

        self.enemies = self._spawn_enemies(level)

    def _spawn_enemies(self, level):
        """Spawn enemies for the current wave."""
        enemies = []

        if self.boss_wave:
            # Boss + some minions
            boss_x = level.width // 2 - 40
            boss_y = level.ground_y - 120
            boss = Boss(boss_x, boss_y, self.boss_number)
            boss.apply_wave_scaling(self.wave_number, WAVE_STAT_SCALE * 0.3)
            enemies.append(boss)

            # Fewer minions during boss
            minion_count = 2 + self.boss_number
            spawn_points = level.get_spawn_points(minion_count)
            for i, (x, y) in enumerate(spawn_points):
                enemy = Grunt(x, y)
                enemy.apply_wave_scaling(self.wave_number, WAVE_STAT_SCALE)
                enemies.append(enemy)
        else:
            # Normal wave — mix of enemy types based on wave number
            count = int(WAVE_ENEMY_BASE_COUNT +
                        self.wave_number * WAVE_ENEMY_SCALE)
            count = min(count, 20)  # Cap

            spawn_points = level.get_spawn_points(count)

            for i, (x, y) in enumerate(spawn_points):
                enemy = self._pick_enemy_type(x, y)
                enemy.apply_wave_scaling(self.wave_number, WAVE_STAT_SCALE)
                enemies.append(enemy)

        return enemies

    def _pick_enemy_type(self, x, y):
        """Pick enemy type based on wave number."""
        wave = self.wave_number

        if wave <= 3:
            # Only grunts
            return Grunt(x, y)
        elif wave <= 6:
            # Grunts + Runners
            if random.random() < 0.4:
                return Runner(x, y)
            return Grunt(x, y)
        elif wave <= 9:
            # Grunts + Runners + Heavies
            r = random.random()
            if r < 0.15:
                return Heavy(x, y)
            elif r < 0.45:
                return Runner(x, y)
            return Grunt(x, y)
        else:
            # All types, increasing difficulty
            cycle_wave = wave % BOSS_WAVE_INTERVAL
            r = random.random()
            heavy_chance = min(0.3, 0.1 + wave * 0.01)
            runner_chance = min(0.4, 0.25 + wave * 0.005)

            if r < heavy_chance:
                return Heavy(x, y)
            elif r < heavy_chance + runner_chance:
                return Runner(x, y)
            return Grunt(x, y)

    def update(self):
        """Check if wave is complete."""
        if self.wave_active:
            alive_enemies = [e for e in self.enemies if e.alive]
            if len(alive_enemies) == 0:
                self.wave_active = False
                self.wave_complete = True
                self.between_waves = True

    def get_alive_enemies(self):
        return [e for e in self.enemies if e.alive]

    def is_boss_wave(self):
        return self.boss_wave

    def get_boss(self):
        """Return the boss entity if this is a boss wave."""
        for e in self.enemies:
            if e.enemy_type == "boss":
                return e
        return None
