"""
game.py — Main game state machine and loop.
Wires together all systems: player, enemies, weapons, waves, UI, effects.
"""
import pygame
import math
import time

from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    BOSS_WAVE_INTERVAL
)
from core.input_handler import InputHandler
from core.camera import Camera
from art.backgrounds import Background
from art.effects import EffectsManager
from entities.player import Player
from entities.projectiles import ProjectileManager
from systems.wave_manager import WaveManager
from systems.upgrade_system import UpgradeSystem
from systems.particles import ParticleManager
from level.level_gen import Level
from ui.hud import HUD
from ui.menu import MainMenu
from ui.settings_menu import SettingsMenu
from ui.upgrade_screen import UpgradeScreen
from ui.game_over import GameOverScreen
from ui.pause_menu import PauseMenu


class Game:
    """Main game class — state machine and game loop."""

    # States
    STATE_MENU = "menu"
    STATE_SETTINGS = "settings"
    STATE_SETTINGS_FROM_PAUSE = "settings_pause"
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_UPGRADE = "upgrade"
    STATE_GAME_OVER = "game_over"

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = self.STATE_MENU

        # Input
        self.input_handler = InputHandler()

        # UI screens
        self.main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.settings_menu = SettingsMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.upgrade_screen = UpgradeScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game_over_screen = GameOverScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.hud = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Game objects (initialized on game start)
        self.player = None
        self.camera = None
        self.background = None
        self.effects = None
        self.projectiles = None
        self.wave_manager = None
        self.upgrade_system = None
        self.particles = None
        self.level = None

        # Timing
        self.game_start_time = 0
        self.wave_transition_timer = 0

    def run(self):
        """Main game loop."""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return

            self.input_handler.update()

            # State machine
            if self.state == self.STATE_MENU:
                self._update_menu(events)
            elif self.state == self.STATE_SETTINGS:
                self._update_settings(events)
            elif self.state == self.STATE_SETTINGS_FROM_PAUSE:
                self._update_settings_from_pause(events)
            elif self.state == self.STATE_PLAYING:
                self._update_playing(events)
            elif self.state == self.STATE_PAUSED:
                self._update_paused(events)
            elif self.state == self.STATE_UPGRADE:
                self._update_upgrade(events)
            elif self.state == self.STATE_GAME_OVER:
                self._update_game_over(events)

            pygame.display.flip()
            self.clock.tick(FPS)

    # ─── State handlers ───────────────────────────────────

    def _update_menu(self, events):
        self.main_menu.handle_input(events, self.input_handler)
        self.main_menu.draw(self.screen)

        if self.main_menu.result == "start":
            self._start_new_game()
        elif self.main_menu.result == "settings":
            self.state = self.STATE_SETTINGS
        elif self.main_menu.result == "quit":
            self.running = False

    def _update_settings(self, events):
        self.settings_menu.handle_input(events, self.input_handler)
        self.settings_menu.draw(self.screen)

        if self.settings_menu.result == "back":
            self.state = self.STATE_MENU

    def _update_settings_from_pause(self, events):
        self.settings_menu.handle_input(events, self.input_handler)
        self.settings_menu.draw(self.screen)

        if self.settings_menu.result == "back":
            self.state = self.STATE_PAUSED

    def _update_playing(self, events):
        # Check pause
        if self.input_handler.is_just_pressed("pause"):
            self.state = self.STATE_PAUSED
            return

        # Wave transition
        if self.wave_transition_timer > 0:
            self.wave_transition_timer -= 1
            self._render_game()
            self._draw_wave_transition()
            if self.wave_transition_timer <= 0:
                if self.wave_manager.wave_complete:
                    # Offer upgrades
                    # Speedrun check: < 30s normal wave, < 60s boss wave
                    wave_duration = time.time() - self.wave_start_time
                    time_limit = 60 if self.wave_manager.is_boss_wave() else 30
                    if wave_duration < time_limit:
                        self.upgrade_system.picks_allowed = 2
                    else:
                        self.upgrade_system.picks_allowed = 1

                    upgrades = self.upgrade_system.offer_upgrades()
                    if upgrades:
                        self.upgrade_screen.set_upgrades(upgrades)
                        self.state = self.STATE_UPGRADE
                    else:
                        self._start_next_wave()
            return

        # Update player
        self.player.update(
            self.input_handler,
            self.level.platforms,
            self.level.walls,
            self.level.ground_y,
            self.level.width
        )

        # Parkour Buff check
        if not self.parkour_buff_used and self.player.y < self.level.ground_y - 380:
            self.parkour_buff_used = True
            import random
            buff_type = random.choice(["shield", "regen", "akimbo"])
            if buff_type == "shield":
                self.player.shield_active = True
            elif buff_type == "regen":
                self.player.regen_timer = 600  # 10 secs regen
            elif buff_type == "akimbo":
                self.player.akimbo_timer = 600 # 10 secs akimbo
            self.effects.trigger_white_flash(10)
            self.particles.emit_dust(self.player.center_x, self.player.center_y, 30)
            self.camera.add_shake(8, 12)

        # Update combo
        if self.combo_count > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0

        # Dash trail particles
        if self.player.is_dashing:
            self.particles.emit_dash_trail(
                self.player.x, self.player.y,
                self.player.w, self.player.h
            )

        # Wall slide particles
        if self.player.on_wall and self.player.vel_y > 0:
            wx = self.player.x if self.player.on_wall == 'left' else (
                self.player.x + self.player.w)
            self.particles.emit_wall_slide(wx, self.player.y + self.player.h // 2)

        # Player shooting
        if self.input_handler.shoot_pressed() and self.player.current_weapon.can_fire():
            if self.player.current_weapon.fire():
                mx, my = self.input_handler.get_mouse_pos()
                aim_angle = self.player.get_aim_angle(mx, my, self.camera)
                muzzle_x, muzzle_y = self.player.get_muzzle_pos()
                config = self.player.current_weapon.get_projectile_config()
                self.projectiles.spawn(muzzle_x, muzzle_y, aim_angle, config, True)

                # Effects
                self.particles.emit_muzzle_flash(muzzle_x, muzzle_y, aim_angle)
                self.particles.emit_shell_casing(
                    muzzle_x, muzzle_y, self.player.facing_right
                )
                self.camera.add_shake(3, 5)

        # Update enemies
        for enemy in self.wave_manager.get_alive_enemies():
            enemy.update(
                self.player,
                self.level.platforms,
                self.level.ground_y,
                self.level.width
            )

            # Enemy shooting
            if hasattr(enemy, 'wants_to_shoot') and enemy.wants_to_shoot:
                if enemy.enemy_type == "boss":
                    # Boss spread shot
                    for angle in enemy.shoot_angles:
                        self.projectiles.spawn_enemy_bullet(
                            enemy.center_x, enemy.center_y,
                            angle, speed=4, damage=enemy.damage, size=5
                        )
                    self.camera.add_shake(6, 10)
                elif enemy.enemy_type == "heavy":
                    # Heavy — big bullet
                    self.projectiles.spawn_enemy_bullet(
                        enemy.center_x, enemy.center_y,
                        enemy.shoot_angle,
                        speed=enemy.bullet_speed,
                        damage=enemy.damage,
                        size=6
                    )
                    self.camera.add_shake(5, 8)
                else:
                    # Grunt normal bullet
                    self.projectiles.spawn_enemy_bullet(
                        enemy.center_x, enemy.center_y,
                        enemy.shoot_angle,
                        speed=enemy.bullet_speed,
                        damage=enemy.damage,
                        size=4
                    )

            # Runner melee attack
            if hasattr(enemy, 'wants_to_melee') and enemy.wants_to_melee:
                if self.player.rect.colliderect(enemy.rect.inflate(20, 20)):
                    if self.player.take_damage(1):
                        self.effects.trigger_hit_flash()
                        self.camera.add_shake(5, 8)
                        self.particles.emit_blood(
                            self.player.center_x, self.player.center_y
                        )

            # Boss slam damage
            if enemy.enemy_type == "boss" and hasattr(enemy, 'slam_active'):
                if enemy.slam_active:
                    dist = abs(self.player.center_x - enemy.center_x)
                    if dist < 150 and self.player.on_ground:
                        if self.player.take_damage(2):
                            self.effects.trigger_hit_flash()
                            self.camera.add_shake(8, 12)

            # Boss charge contact damage
            if enemy.enemy_type == "boss":
                if (enemy.current_attack == "charge" and
                        enemy.attack_phase_timer >= 20):
                    if self.player.rect.colliderect(enemy.rect):
                        if self.player.take_damage(2):
                            self.effects.trigger_hit_flash()
                            self.camera.add_shake(6, 10)
                            self.particles.emit_blood(
                                self.player.center_x, self.player.center_y
                            )

        # Projectile collisions
        self._handle_projectile_collisions()

        # Update projectiles
        self.projectiles.update(self.level.width, self.level.height)

        # Update particles
        self.particles.update()

        # Update effects
        self.effects.update()

        # Update camera
        self.camera.follow(
            self.player.center_x, self.player.center_y,
            self.level.width, self.level.height
        )
        self.camera.update()

        # Check wave completion
        self.wave_manager.update()
        if self.wave_manager.wave_complete and self.wave_transition_timer <= 0:
            self.wave_transition_timer = 90  # 1.5 second transition

        # Check player death
        if not self.player.alive:
            elapsed = time.time() - self.game_start_time
            self.game_over_screen.set_stats(
                self.wave_manager.wave_number,
                self.player.kills,
                elapsed
            )
            self.state = self.STATE_GAME_OVER

        # Render
        self._render_game()

    def _update_paused(self, events):
        # Draw game behind pause
        self._render_game()
        self.pause_menu.handle_input(events)
        self.pause_menu.draw(self.screen)

        if self.pause_menu.result == "resume":
            self.state = self.STATE_PLAYING
        elif self.pause_menu.result == "settings":
            self.state = self.STATE_SETTINGS_FROM_PAUSE
        elif self.pause_menu.result == "quit":
            self.state = self.STATE_MENU

    def _update_upgrade(self, events):
        self._render_game()
        self.upgrade_screen.handle_input(events)
        self.upgrade_screen.draw(self.screen)

        if self.upgrade_screen.result is not None:
            self.upgrade_system.select_upgrade(
                self.upgrade_screen.result, self.player
            )
            
            if self.upgrade_system.picks_allowed > 1 and len(self.upgrade_system.offered_upgrades) > 0:
                self.upgrade_system.picks_allowed -= 1
                self.upgrade_screen.result = None
                self.upgrade_screen.set_upgrades(self.upgrade_system.offered_upgrades)
            else:
                self.state = self.STATE_PLAYING
                self._start_next_wave()

    def _update_game_over(self, events):
        self.game_over_screen.handle_input(events)
        self.game_over_screen.draw(self.screen)

        if self.game_over_screen.result == "retry":
            self._start_new_game()
        elif self.game_over_screen.result == "menu":
            self.state = self.STATE_MENU

    # ─── Game logic ───────────────────────────────────────

    def _start_new_game(self):
        """Initialize a new game."""
        level_w = 1400
        level_h = SCREEN_HEIGHT + 200
        ground_y = SCREEN_HEIGHT - 80

        self.level = Level(level_w, level_h, ground_y)
        self.player = Player(level_w // 2 - 18, ground_y - 60)
        self.camera = Camera()
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.effects = EffectsManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.projectiles = ProjectileManager()
        self.wave_manager = WaveManager()
        self.upgrade_system = UpgradeSystem()
        self.particles = ParticleManager()
        self.game_start_time = time.time()
        self.wave_transition_timer = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.wave_start_time = time.time()
        self.parkour_buff_used = False

        self.state = self.STATE_PLAYING
        self._start_next_wave()

    def _start_next_wave(self):
        """Start the next wave."""
        self.level.generate(self.wave_manager.wave_number + 1)
        self.wave_manager.start_wave(self.level)
        self.wave_start_time = time.time()
        self.parkour_buff_used = False
        self.player.shield_active = False

        # Boss warning
        if self.wave_manager.is_boss_wave():
            self.effects.trigger_boss_warning(self.wave_manager.wave_number)

        # Refill weapons
        self.player.deagle.reset()
        self.player.shotgun.reset()

    def _handle_projectile_collisions(self):
        """Check all projectile-entity collisions."""
        # Player projectiles vs enemies
        for proj in self.projectiles.get_player_projectiles():
            for enemy in self.wave_manager.get_alive_enemies():
                if proj.alive and enemy.alive and proj.rect.colliderect(enemy.rect):
                    killed = enemy.take_damage(proj.damage)
                    proj.on_hit()

                    # Effects
                    self.effects.add_damage_number(
                        enemy.center_x, enemy.y - 5,
                        proj.damage, (255, 255, 100)
                    )
                    self.particles.emit_blood(
                        proj.x, proj.y, count=6
                    )
                    self.camera.add_shake(2, 3)

                    if killed:
                        self.player.kills += 1
                        self.combo_count += 1
                        self.combo_timer = 300
                        self.particles.emit_death_explosion(
                            enemy.center_x, enemy.center_y
                        )
                        self.camera.add_shake(4, 6)
                        
                        if self.combo_count > 5:
                            for _ in range(self.combo_count // 5):
                                self.particles.emit_dash_trail(self.player.x, self.player.y, self.player.w, self.player.h)

                        # Boss kill — big effects
                        if enemy.enemy_type == "boss":
                            self.effects.trigger_white_flash(12)
                            self.effects.trigger_slow_mo(45)
                            self.camera.add_shake(10, 15)

        # Enemy projectiles vs player
        for proj in self.projectiles.get_enemy_projectiles():
            if proj.alive and self.player.alive:
                if proj.rect.colliderect(self.player.rect):
                    if self.player.parry_timer > 0:
                        # Deflect
                        proj.vel_x *= -1.5
                        proj.vel_y *= -1.5
                        proj.damage *= 2
                        proj.is_player = True
                        self.effects.trigger_white_flash(5)
                        self.particles.emit_muzzle_flash(self.player.center_x, self.player.center_y, 0, count=10)
                        self.camera.add_shake(6, 8)
                    else:
                        if self.player.take_damage(1):
                            self.combo_count = 0
                            self.effects.trigger_hit_flash()
                            self.camera.add_shake(12, 15)  # Heavy screen shake
                            self.particles.emit_blood(
                                self.player.center_x,
                                self.player.center_y, count=20 # Extra blood
                            )
                        proj.alive = False

        # Contact damage from enemies touching player
        for enemy in self.wave_manager.get_alive_enemies():
            if enemy.alive and self.player.alive:
                if enemy.enemy_type not in ("boss",):  # Boss handled separately
                    if (enemy.rect.colliderect(self.player.rect) and
                            enemy.enemy_type == "runner" and
                            enemy.state == "chase"):
                        # Runner contact while charging
                        pass  # Handled via wants_to_melee

    # ─── Rendering ────────────────────────────────────────

    def _render_game(self):
        """Render the full game scene."""
        # Background
        self.background.draw(
            self.screen, self.camera.x,
            self.wave_manager.wave_number if self.wave_manager else 1
        )

        # Level
        self.level.draw(self.screen, self.camera)

        # Particles (behind entities)
        self.particles.draw(self.screen, self.camera)

        # Enemies
        for enemy in self.wave_manager.get_alive_enemies():
            enemy.draw(self.screen, self.camera)

        # Player
        self.player.draw(self.screen, self.camera)

        # Projectiles
        self.projectiles.draw(self.screen, self.camera)

        # Effects overlay
        self.effects.draw(self.screen, self.camera)

        # HUD
        self.hud.draw(
            self.screen, self.player,
            self.wave_manager.wave_number,
            self.player.weapon_type,
            self.combo_count,
            self.combo_timer
        )

    def _draw_wave_transition(self):
        """Draw wave transition effect."""
        font = pygame.font.Font(None, 52)
        if self.wave_manager.wave_complete:
            text = f"WAVE {self.wave_manager.wave_number} CLEARED!"
            color = (100, 200, 100)
        else:
            next_wave = self.wave_manager.wave_number
            if next_wave % BOSS_WAVE_INTERVAL == 0:
                text = f"BOSS WAVE {next_wave}!"
                color = (200, 50, 50)
            else:
                text = f"WAVE {next_wave}"
                color = (218, 175, 65)

        # Fade
        alpha = 255
        if self.wave_transition_timer > 70:
            alpha = int(255 * (90 - self.wave_transition_timer) / 20)
        elif self.wave_transition_timer < 20:
            alpha = int(255 * self.wave_transition_timer / 20)

        text_surf = font.render(text, True, color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        shadow = font.render(text, True, (20, 15, 10))
        shadow.set_alpha(alpha)
        self.screen.blit(shadow, (rect.x + 2, rect.y + 2))
        self.screen.blit(text_surf, rect)
