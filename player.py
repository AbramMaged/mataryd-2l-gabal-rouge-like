"""
player.py — Player entity: Egyptian farmer protagonist.
Handles movement, jumping, wall jumping, dashing, crouching, stamina, and weapons.
"""
import pygame
import math
from core.settings import (
    PLAYER_SPEED, PLAYER_ACCEL, PLAYER_WIDTH, PLAYER_HEIGHT,
    PLAYER_CROUCH_HEIGHT, PLAYER_JUMP_FORCE,
    PLAYER_WALL_JUMP_FORCE_X, PLAYER_WALL_JUMP_FORCE_Y,
    PLAYER_MAX_HEARTS, PLAYER_COYOTE_TIME,
    DASH_SPEED, DASH_DURATION, DASH_COOLDOWN, DASH_IFRAMES,
    STARTING_STAMINA, MAX_STAMINA
)
from physics.physics import apply_gravity, apply_friction
from physics.collision import (
    check_platform_collision, check_wall_collision, check_ground_collision
)
from weapons.deagle import Deagle
from weapons.shotgun import Shotgun
from art.sprites import draw_player
from art.animations import Animator, AnimationState


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.facing_right = True
        self.on_ground = False
        self.on_wall = None  # 'left' or 'right' or None
        self.is_crouching = False

        # Jump
        self.can_jump = False
        self.coyote_timer = 0
        self.jump_buffer = 0  # frames remaining of buffered jump input

        # Wall jump
        self.wall_jump_cooldown = 0  # frames to skip speed clamp after wall jump
        self.last_wall_jumped = None # 'left' or 'right'

        # Parry
        self.parry_timer = 0
        self.parry_duration = 15

        # Dash
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_dir = 1
        self.dash_iframes = 0  # invincibility frames from dash

        # Stamina (for dashing)
        self.max_stamina = STARTING_STAMINA
        self.stamina = STARTING_STAMINA
        self.stamina_recharge_timer = 0
        self.stamina_recharge_rate = DASH_COOLDOWN

        # Health (poker heart cards)
        self.max_hearts = PLAYER_MAX_HEARTS
        self.hearts = PLAYER_MAX_HEARTS
        self.invincible_timer = 0  # i-frames after getting hit
        
        # Buffs
        self.shield_active = False
        self.regen_timer = 0
        self.akimbo_timer = 0

        # Weapons
        self.deagle = Deagle()
        self.shotgun = Shotgun()
        self.current_weapon = self.deagle
        self.weapon_type = "deagle"  # "deagle" or "shotgun"

        # Animation
        self.animator = Animator()
        self.hurt_timer = 0

        # Stats
        self.speed_mult = 1.0
        self.kills = 0
        self.alive = True

        # Heart flip animation tracking
        self.heart_flip_timers = [0] * self.max_hearts

    @property
    def rect(self):
        h = PLAYER_CROUCH_HEIGHT if self.is_crouching else self.h
        return pygame.Rect(int(self.x), int(self.y), self.w, h)

    @property
    def center_x(self):
        return self.x + self.w / 2

    @property
    def center_y(self):
        h = PLAYER_CROUCH_HEIGHT if self.is_crouching else self.h
        return self.y + h / 2

    def update(self, input_handler, platforms, walls, ground_y, level_width):
        if not self.alive:
            return

        # ─── Timers ───────────────────────────────
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.dash_iframes > 0:
            self.dash_iframes -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown -= 1
        if self.parry_timer > 0:
            self.parry_timer -= 1
            
        # Buffs
        if self.akimbo_timer > 0:
            self.akimbo_timer -= 1
        if self.regen_timer > 0:
            self.regen_timer -= 1
            if self.regen_timer % 120 == 0:  # Heal 1 heart every 2 seconds
                self.heal(1)
                
        # Update dynamic fire rate multiplier (akimbo)
        target_fire_mult = 2.0 if self.akimbo_timer > 0 else 1.0
        self.current_weapon.fire_rate_mult = max(self.current_weapon.fire_rate_mult, target_fire_mult)

        # Stamina recharge
        if self.stamina < self.max_stamina:
            self.stamina_recharge_timer += 1
            if self.stamina_recharge_timer >= self.stamina_recharge_rate:
                self.stamina += 1
                self.stamina_recharge_timer = 0

        # Heart flip timers
        for i in range(len(self.heart_flip_timers)):
            if self.heart_flip_timers[i] > 0:
                self.heart_flip_timers[i] -= 1

        # ─── Dashing ─────────────────────────────
        if self.is_dashing:
            self.dash_timer -= 1
            self.vel_x = DASH_SPEED * self.dash_dir
            self.vel_y = 0
            if self.dash_timer <= 0:
                self.is_dashing = False
            self._apply_position(platforms, walls, ground_y, level_width)
            self.animator.set_state(AnimationState.DASH)
            self.animator.update()
            return

        # ─── Horizontal movement ──────────────────
        move_speed = PLAYER_SPEED * self.speed_mult
        if self.is_crouching:
            move_speed *= 0.4

        if input_handler.is_held("move_left"):
            self.vel_x -= PLAYER_ACCEL
            self.facing_right = False
        elif input_handler.is_held("move_right"):
            self.vel_x += PLAYER_ACCEL
            self.facing_right = True

        # Clamp horizontal speed — BUT skip if wall jump cooldown is active
        # so the wall jump force isn't immediately killed
        if self.wall_jump_cooldown <= 0:
            if abs(self.vel_x) > move_speed:
                self.vel_x = move_speed if self.vel_x > 0 else -move_speed
        else:
            # Gentle decel during wall jump — don't hard clamp
            max_wj_speed = PLAYER_WALL_JUMP_FORCE_X
            if abs(self.vel_x) > max_wj_speed:
                self.vel_x = max_wj_speed if self.vel_x > 0 else -max_wj_speed

        # Apply friction
        if not input_handler.is_held("move_left") and not input_handler.is_held("move_right"):
            self.vel_x = apply_friction(self.vel_x, self.on_ground)

        # ─── Crouch ───────────────────────────────
        if input_handler.is_held("crouch") and self.on_ground:
            if not self.is_crouching:
                self.is_crouching = True
                # Adjust y position so feet stay on ground
                self.y += (PLAYER_HEIGHT - PLAYER_CROUCH_HEIGHT)
        else:
            self.is_crouching = False

        # ─── Jump buffer ─────────────────────────
        # Store jump input for a few frames so you don't need pixel-perfect timing
        if input_handler.jump_pressed():
            self.jump_buffer = 8  # remember jump press for 8 frames
        elif self.jump_buffer > 0:
            self.jump_buffer -= 1

        # ─── Jump ─────────────────────────────────
        # Coyote time
        if self.on_ground:
            self.coyote_timer = PLAYER_COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        if self.jump_buffer > 0:
            if self.coyote_timer > 0:
                # Normal jump
                self.vel_y = PLAYER_JUMP_FORCE
                self.coyote_timer = 0
                self.on_ground = False
                self.jump_buffer = 0
            elif self.on_wall is not None and self.on_wall != self.last_wall_jumped:
                # Wall jump — can do it whenever touching a wall, but not the SAME wall successively
                wall_dir = -1 if self.on_wall == 'right' else 1
                self.vel_x = PLAYER_WALL_JUMP_FORCE_X * wall_dir
                self.vel_y = PLAYER_WALL_JUMP_FORCE_Y
                self.facing_right = wall_dir > 0
                self.last_wall_jumped = self.on_wall
                self.on_wall = None
                self.jump_buffer = 0
                self.wall_jump_cooldown = 12  # frames to preserve wall jump velocity

        # ─── Parry ────────────────────────────────
        if input_handler.parry_just_pressed() and self.parry_timer <= 0:
            if self.stamina > 0:
                self.parry_timer = self.parry_duration
                self.stamina -= 1
                self.stamina_recharge_timer = 0

        # ─── Dash ─────────────────────────────────
        if input_handler.is_just_pressed("dash") and not self.is_dashing:
            if self.stamina > 0:
                self.is_dashing = True
                self.dash_timer = DASH_DURATION
                self.dash_dir = 1 if self.facing_right else -1
                self.dash_iframes = DASH_IFRAMES
                self.stamina -= 1
                self.stamina_recharge_timer = 0

        # ─── Gravity ─────────────────────────────
        self.vel_y = apply_gravity(self.vel_y)

        # Wall slide (slow fall when touching wall)
        if self.on_wall and self.vel_y > 0:
            self.vel_y = min(self.vel_y, 3)

        # ─── Apply position ───────────────────────
        self._apply_position(platforms, walls, ground_y, level_width)

        # ─── Weapon update ────────────────────────
        self.current_weapon.update()

        # Auto-reload when empty
        if self.current_weapon.current_ammo <= 0 and not self.current_weapon.is_reloading:
            self.current_weapon.start_reload()

        # Manual reload
        if input_handler.is_just_pressed("reload"):
            self.current_weapon.start_reload()

        # Weapon switch
        if input_handler.is_just_pressed("weapon_1"):
            self._switch_weapon("deagle")
        elif input_handler.is_just_pressed("weapon_2"):
            self._switch_weapon("shotgun")
        elif input_handler.is_just_pressed("switch_weapon"):
            if self.weapon_type == "deagle":
                self._switch_weapon("shotgun")
            else:
                self._switch_weapon("deagle")

        # ─── Animation state ─────────────────────
        self._update_animation()

    def _apply_position(self, platforms, walls, ground_y, level_width):
        """Apply velocity to position and handle collisions."""
        # Horizontal
        self.x += self.vel_x

        # Wall collision FIRST (before boundary clamp so wall-jump detection works)
        self.on_wall = check_wall_collision(self.rect, walls)

        # Push out of solid wall overlap
        if self.on_wall == 'right':
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.x = wall.rect.left - self.w
                    self.vel_x = 0
        elif self.on_wall == 'left':
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.x = wall.rect.right
                    self.vel_x = 0

        # Level bounds (after wall check so on_wall is preserved)
        if self.x < 2:
            self.x = 2
            if self.vel_x < 0:
                self.vel_x = 0
        elif self.x + self.w > level_width - 2:
            self.x = level_width - 2 - self.w
            if self.vel_x > 0:
                self.vel_x = 0

        # Can't wall-jump while on ground
        if self.on_ground:
            self.on_wall = None

        # Vertical
        self.y += self.vel_y

        # Ground collision
        landed, new_y = check_ground_collision(self.rect, self.vel_y, ground_y)
        if landed:
            self.y = new_y
            self.vel_y = 0
            self.on_ground = True
            self.last_wall_jumped = None
        else:
            # Platform collision
            landed, new_y, _ = check_platform_collision(
                self.rect, self.vel_y, platforms
            )
            if landed:
                self.y = new_y
                self.vel_y = 0
                self.on_ground = True
            else:
                self.on_ground = False

    def _switch_weapon(self, weapon_type):
        if weapon_type == self.weapon_type:
            return
        self.weapon_type = weapon_type
        if weapon_type == "deagle":
            self.current_weapon = self.deagle
        else:
            self.current_weapon = self.shotgun

    def _update_animation(self):
        if self.hurt_timer > 0:
            self.animator.set_state(AnimationState.HURT)
        elif self.is_crouching:
            self.animator.set_state(AnimationState.CROUCH)
        elif not self.on_ground:
            if self.on_wall:
                self.animator.set_state(AnimationState.WALL_SLIDE)
            elif self.vel_y < 0:
                self.animator.set_state(AnimationState.JUMP)
            else:
                self.animator.set_state(AnimationState.FALL)
        elif abs(self.vel_x) > 0.5:
            self.animator.set_state(AnimationState.RUN)
        else:
            self.animator.set_state(AnimationState.IDLE)
        self.animator.update()

    def take_damage(self, damage_hearts=1):
        """Player takes damage. Returns True if damage was applied."""
        if self.invincible_timer > 0 or self.dash_iframes > 0:
            return False

        if self.shield_active:
            self.shield_active = False
            self.invincible_timer = 30
            return False # Absorbed the hit

        self.hearts -= damage_hearts
        self.hurt_timer = 15
        self.invincible_timer = 45  # Brief invincibility after hit

        # Trigger heart flip animation
        flip_index = self.hearts  # The heart that just got lost
        if 0 <= flip_index < len(self.heart_flip_timers):
            self.heart_flip_timers[flip_index] = 20

        if self.hearts <= 0:
            self.hearts = 0
            self.alive = False

        return True

    def heal(self, amount=1):
        """Restore hearts."""
        self.hearts = min(self.max_hearts, self.hearts + amount)

    def get_aim_angle(self, mouse_x, mouse_y, camera):
        """Get angle from player to mouse in world coords."""
        cam_offset = camera.get_offset()
        world_mx = mouse_x + cam_offset[0]
        world_my = mouse_y + cam_offset[1]
        dx = world_mx - self.center_x
        dy = world_my - self.center_y
        return math.atan2(dy, dx)

    def get_muzzle_pos(self):
        """Get the position where bullets spawn."""
        offset_x = 30 if self.facing_right else -10
        offset_y = self.h * 0.35
        return (self.x + offset_x, self.y + offset_y)

    def draw(self, surface, camera):
        if not self.alive:
            return

        sx, sy = camera.apply(self.x, self.y)

        # Shield aura
        if self.shield_active:
            pygame.draw.circle(surface, (100, 255, 150), (int(sx + self.w//2), int(sy + self.h//2)), int(self.h * 0.9), 2)

        # Invincibility blink
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            return  # Blink effect

        # Parry visual
        if self.parry_timer > 0:
            pygame.draw.circle(surface, (150, 200, 255), (int(sx + self.w//2), int(sy + self.h//2)), int(self.h * 0.8), 2)

        h = PLAYER_CROUCH_HEIGHT if self.is_crouching else self.h
        draw_player(
            surface, sx, sy, self.w, h,
            self.facing_right,
            self.animator.state,
            self.animator.get_frame(),
            self.is_crouching,
            self.weapon_type,
            0,  # aim angle
            self.current_weapon.fire_timer,
            max(1, self.current_weapon.fire_rate / self.current_weapon.fire_rate_mult)
        )
