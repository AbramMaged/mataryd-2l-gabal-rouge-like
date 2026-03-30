"""
sprites.py — Procedural sprite drawing for all entities.
All characters are drawn with Pygame primitives (no image files).
Swap this file to change the entire art style.
"""
import pygame
import math
from art.colors import *
from art.animations import AnimationState


def draw_player(surface, x, y, w, h, facing_right, anim_state, anim_frame,
                is_crouching=False, weapon_type="deagle", aim_angle=0,
                weapon_fire_timer=0, weapon_fire_rate=1):
    """Draw the Egyptian farmer protagonist."""
    # Body offset for animation
    bob_y = 0
    if anim_state == AnimationState.RUN:
        bob_y = int(math.sin(anim_frame * 1.2) * 3)
    elif anim_state == AnimationState.DASH:
        bob_y = -2

    bx, by = int(x), int(y + bob_y)

    # Galabiya (robe) — main body
    robe_rect = pygame.Rect(bx + w * 0.2, by + h * 0.3, w * 0.6, h * 0.65)
    pygame.draw.rect(surface, GALABIYA_WHITE, robe_rect)
    pygame.draw.rect(surface, GALABIYA_SHADOW, robe_rect, 2)

    # Shadow on robe
    shadow_rect = pygame.Rect(
        bx + (w * 0.2 if facing_right else w * 0.4),
        by + h * 0.35, w * 0.2, h * 0.55
    )
    pygame.draw.rect(surface, GALABIYA_SHADOW, shadow_rect)

    # Head
    head_cx = bx + w // 2
    head_cy = by + int(h * 0.18)
    head_r = int(w * 0.28)
    pygame.draw.circle(surface, SKIN_DARK, (head_cx, head_cy), head_r)

    # Headwrap
    wrap_rect = pygame.Rect(head_cx - head_r, head_cy - head_r,
                            head_r * 2, int(head_r * 0.9))
    pygame.draw.rect(surface, HEADWRAP, wrap_rect)
    pygame.draw.rect(surface, HEADWRAP_SHADOW, wrap_rect, 1)

    # Eyes
    eye_offset = 3 if facing_right else -3
    eye_y = head_cy + 2
    pygame.draw.circle(surface, (255, 255, 255), (head_cx + eye_offset, eye_y), 3)
    pupil_off = 1 if facing_right else -1
    pygame.draw.circle(surface, (20, 20, 20),
                       (head_cx + eye_offset + pupil_off, eye_y), 1)

    # Legs (animated for running)
    leg_y = by + int(h * 0.85)
    if anim_state == AnimationState.RUN:
        leg_spread = int(math.sin(anim_frame * 1.5) * 6)
        left_leg_x = bx + w * 0.3 - leg_spread
        right_leg_x = bx + w * 0.6 + leg_spread
    else:
        left_leg_x = bx + w * 0.3
        right_leg_x = bx + w * 0.6

    # Sandals / feet
    pygame.draw.rect(surface, DIRT_DARK,
                     (int(left_leg_x), leg_y, 8, 12))
    pygame.draw.rect(surface, DIRT_DARK,
                     (int(right_leg_x), leg_y, 8, 12))
    # Skin for legs
    pygame.draw.rect(surface, SKIN_DARK,
                     (int(left_leg_x) + 1, leg_y - 4, 6, 8))
    pygame.draw.rect(surface, SKIN_DARK,
                     (int(right_leg_x) + 1, leg_y - 4, 6, 8))

    # Arms + Weapon
    arm_y = by + int(h * 0.4)
    if facing_right:
        arm_x = bx + w * 0.7
    else:
        arm_x = bx + w * 0.1

    # Arm (dark skin)
    arm_w = 8
    arm_h = 6
    pygame.draw.rect(surface, SKIN_DARK,
                     (int(arm_x), arm_y, arm_w, arm_h))

    # Weapon
    _draw_weapon(surface, arm_x, arm_y, facing_right, weapon_type, aim_angle, weapon_fire_timer, weapon_fire_rate)


def _draw_weapon(surface, arm_x, arm_y, facing_right, weapon_type, aim_angle, fire_timer=0, fire_rate=1):
    """Draw weapon at arm position. Shotgun flips when fired."""
    wx = int(arm_x) + (8 if facing_right else -16)
    wy = int(arm_y) - 2

    if weapon_type == "deagle":
        # Deagle — compact pistol shape
        barrel_len = 16
        body_w = 14
        body_h = 8
        if facing_right:
            pygame.draw.rect(surface, (60, 60, 65), (wx, wy, barrel_len, 4))
            pygame.draw.rect(surface, (45, 45, 50), (wx - 2, wy, body_w, body_h))
            # Grip
            pygame.draw.rect(surface, WOOD_DARK, (wx, wy + body_h - 2, 5, 8))
        else:
            pygame.draw.rect(surface, (60, 60, 65),
                             (wx - barrel_len + 16, wy, barrel_len, 4))
            pygame.draw.rect(surface, (45, 45, 50),
                             (wx + 4, wy, body_w, body_h))
            pygame.draw.rect(surface, WOOD_DARK,
                             (wx + 12, wy + body_h - 2, 5, 8))
    else:
        # Shotgun — longer barrel, pump grip
        barrel_len = 28
        
        # Determine flip angle based on fire timer
        flip_angle = 0
        if weapon_type == "shotgun" and fire_timer > 0:
            progress = 1.0 - (fire_timer / fire_rate)
            # full 360 flip
            flip_angle = progress * 360
            if not facing_right:
                flip_angle = -flip_angle

        # Draw to a temp surface to allow rotation
        w_surf_size = 40
        w_surf = pygame.Surface((w_surf_size, w_surf_size), pygame.SRCALPHA)
        center_x, center_y = w_surf_size // 2, w_surf_size // 2
        
        if facing_right:
            pygame.draw.rect(w_surf, (55, 55, 60), (center_x - 8, center_y - 2, barrel_len, 4))
            pygame.draw.rect(w_surf, (45, 45, 50), (center_x - 10, center_y - 3, 12, 6))
            pygame.draw.rect(w_surf, WOOD, (center_x, center_y + 1, 10, 4))
            pygame.draw.rect(w_surf, WOOD_DARK, (center_x - 14, center_y - 2, 6, 5))
        else:
            pygame.draw.rect(w_surf, (55, 55, 60), (center_x - barrel_len + 8, center_y - 2, barrel_len, 4))
            pygame.draw.rect(w_surf, (45, 45, 50), (center_x - 2, center_y - 3, 12, 6))
            pygame.draw.rect(w_surf, WOOD, (center_x - 10, center_y + 1, 10, 4))
            pygame.draw.rect(w_surf, WOOD_DARK, (center_x + 8, center_y - 2, 6, 5))
            
        if flip_angle != 0:
            rotated_surf = pygame.transform.rotate(w_surf, flip_angle)
            rot_rect = rotated_surf.get_rect(center=(wx, wy + 2))
            surface.blit(rotated_surf, rot_rect.topleft)
        else:
            surface.blit(w_surf, (wx - center_x, wy - center_y + 2))


def draw_grunt(surface, x, y, w, h, facing_right, anim_state, anim_frame):
    """Draw grunt enemy — basic soldier type."""
    bx, by = int(x), int(y)

    # Body
    body_rect = pygame.Rect(bx + 4, by + h * 0.25, w - 8, h * 0.55)
    pygame.draw.rect(surface, ENEMY_GRUNT, body_rect)
    pygame.draw.rect(surface, ENEMY_GRUNT_DARK, body_rect, 2)

    # Head
    head_cx = bx + w // 2
    head_cy = by + int(h * 0.15)
    pygame.draw.circle(surface, ENEMY_GRUNT, (head_cx, head_cy), int(w * 0.25))
    pygame.draw.circle(surface, ENEMY_GRUNT_DARK,
                       (head_cx, head_cy), int(w * 0.25), 2)

    # Eyes (angry)
    eye_y = head_cy
    pygame.draw.rect(surface, (200, 50, 50),
                     (head_cx - 5, eye_y - 2, 4, 3))
    pygame.draw.rect(surface, (200, 50, 50),
                     (head_cx + 2, eye_y - 2, 4, 3))

    # Legs
    bob = int(math.sin(anim_frame * 1.3) * 4) if anim_state == AnimationState.RUN else 0
    pygame.draw.rect(surface, ENEMY_GRUNT_DARK,
                     (bx + 8, by + h * 0.75, 8, h * 0.25 + bob))
    pygame.draw.rect(surface, ENEMY_GRUNT_DARK,
                     (bx + w - 16, by + h * 0.75, 8, h * 0.25 - bob))

    # Gun
    gun_y = by + int(h * 0.4)
    if facing_right:
        pygame.draw.rect(surface, (60, 60, 60), (bx + w - 4, gun_y, 14, 3))
    else:
        pygame.draw.rect(surface, (60, 60, 60), (bx - 10, gun_y, 14, 3))


def draw_runner(surface, x, y, w, h, facing_right, anim_state, anim_frame):
    """Draw runner enemy — lean, fast, melee."""
    bx, by = int(x), int(y)

    # Leaning body
    lean = 4 if facing_right else -4
    body_points = [
        (bx + w * 0.3 + lean, by + h * 0.2),
        (bx + w * 0.7 + lean, by + h * 0.2),
        (bx + w * 0.7, by + h * 0.75),
        (bx + w * 0.3, by + h * 0.75),
    ]
    pygame.draw.polygon(surface, ENEMY_RUNNER, body_points)
    pygame.draw.polygon(surface, ENEMY_RUNNER_DARK, body_points, 2)

    # Head
    head_cx = bx + w // 2 + lean
    head_cy = by + int(h * 0.12)
    pygame.draw.circle(surface, ENEMY_RUNNER, (int(head_cx), int(head_cy)), int(w * 0.22))

    # Glowing eyes
    pygame.draw.circle(surface, (220, 100, 255),
                       (int(head_cx - 3), int(head_cy)), 2)
    pygame.draw.circle(surface, (220, 100, 255),
                       (int(head_cx + 4), int(head_cy)), 2)

    # Melee weapon (blade)
    if facing_right:
        blade_x = bx + w + 2
        blade_swing = int(math.sin(anim_frame * 2) * 8)
        pygame.draw.line(surface, (180, 180, 190),
                         (blade_x, by + h * 0.3),
                         (blade_x + 12, by + h * 0.3 + blade_swing), 3)
    else:
        blade_x = bx - 2
        blade_swing = int(math.sin(anim_frame * 2) * 8)
        pygame.draw.line(surface, (180, 180, 190),
                         (blade_x, by + h * 0.3),
                         (blade_x - 12, by + h * 0.3 + blade_swing), 3)

    # Fast legs
    bob = int(math.sin(anim_frame * 2.5) * 6)
    pygame.draw.rect(surface, ENEMY_RUNNER_DARK,
                     (bx + 6, by + h * 0.75, 6, h * 0.25 + bob))
    pygame.draw.rect(surface, ENEMY_RUNNER_DARK,
                     (bx + w - 12, by + h * 0.75, 6, h * 0.25 - bob))


def draw_heavy(surface, x, y, w, h, facing_right, anim_state, anim_frame):
    """Draw heavy enemy — large, armored tank."""
    bx, by = int(x), int(y)

    # Big body
    body_rect = pygame.Rect(bx + 4, by + h * 0.2, w - 8, h * 0.65)
    pygame.draw.rect(surface, ENEMY_HEAVY, body_rect)
    pygame.draw.rect(surface, ENEMY_HEAVY_DARK, body_rect, 3)

    # Armor plates
    pygame.draw.rect(surface, (70, 75, 85),
                     (bx + 8, by + h * 0.25, w - 16, h * 0.15))
    pygame.draw.rect(surface, (90, 95, 110),
                     (bx + 8, by + h * 0.25, w - 16, h * 0.15), 2)

    # Head (smaller relative to body)
    head_cx = bx + w // 2
    head_cy = by + int(h * 0.12)
    pygame.draw.circle(surface, ENEMY_HEAVY,
                       (head_cx, head_cy), int(w * 0.2))
    pygame.draw.circle(surface, ENEMY_HEAVY_DARK,
                       (head_cx, head_cy), int(w * 0.2), 2)

    # Visor eyes
    pygame.draw.rect(surface, (200, 60, 60),
                     (head_cx - 7, head_cy - 1, 14, 3))

    # Heavy weapon
    wep_y = by + int(h * 0.35)
    if facing_right:
        pygame.draw.rect(surface, (50, 50, 55), (bx + w - 2, wep_y, 20, 6))
        pygame.draw.rect(surface, (40, 40, 45), (bx + w - 2, wep_y + 5, 8, 4))
    else:
        pygame.draw.rect(surface, (50, 50, 55), (bx - 18, wep_y, 20, 6))
        pygame.draw.rect(surface, (40, 40, 45), (bx + 10, wep_y + 5, 8, 4))

    # Thick legs
    pygame.draw.rect(surface, ENEMY_HEAVY_DARK,
                     (bx + 8, by + h * 0.8, 12, h * 0.2))
    pygame.draw.rect(surface, ENEMY_HEAVY_DARK,
                     (bx + w - 20, by + h * 0.8, 12, h * 0.2))

    # Cooldown indicator
    if anim_state == AnimationState.COOLDOWN:
        # Breathing/exhausted visual — pulsing
        pulse = int(abs(math.sin(anim_frame * 0.5)) * 4)
        pygame.draw.circle(surface, (150, 150, 50),
                           (head_cx, head_cy - int(h * 0.05)), pulse + 2, 1)


def draw_boss(surface, x, y, w, h, facing_right, anim_state, anim_frame, phase=1):
    """Draw boss enemy — massive Egyptian warrior."""
    bx, by = int(x), int(y)

    # Big body with gold trim
    body_color = ENEMY_BOSS if phase == 1 else (200, 40, 40)
    body_rect = pygame.Rect(bx + 8, by + h * 0.2, w - 16, h * 0.6)
    pygame.draw.rect(surface, body_color, body_rect)
    pygame.draw.rect(surface, ENEMY_BOSS_DARK, body_rect, 3)

    # Gold armor accents
    pygame.draw.rect(surface, ENEMY_BOSS_GOLD,
                     (bx + 12, by + h * 0.22, w - 24, 6))
    pygame.draw.rect(surface, ENEMY_BOSS_GOLD,
                     (bx + 12, by + h * 0.7, w - 24, 6))

    # Egyptian-style head/helmet
    head_cx = bx + w // 2
    head_cy = by + int(h * 0.1)
    head_r = int(w * 0.22)
    pygame.draw.circle(surface, body_color, (head_cx, head_cy), head_r)

    # Pharaoh headdress / nemes
    headdress_points = [
        (head_cx - head_r - 6, head_cy - 2),
        (head_cx, head_cy - head_r - 10),
        (head_cx + head_r + 6, head_cy - 2),
        (head_cx + head_r + 4, head_cy + head_r),
        (head_cx - head_r - 4, head_cy + head_r),
    ]
    pygame.draw.polygon(surface, ENEMY_BOSS_GOLD, headdress_points)
    pygame.draw.polygon(surface, UI_GOLD_DARK, headdress_points, 2)

    # Glowing eyes
    eye_color = (255, 100, 50) if phase == 1 else (255, 50, 50)
    eye_size = 3 if phase == 1 else 4
    pygame.draw.circle(surface, eye_color,
                       (head_cx - 6, head_cy + 2), eye_size)
    pygame.draw.circle(surface, eye_color,
                       (head_cx + 6, head_cy + 2), eye_size)

    # Arms
    arm_y = by + int(h * 0.35)
    pygame.draw.rect(surface, body_color,
                     (bx - 4, arm_y, 16, 12))
    pygame.draw.rect(surface, body_color,
                     (bx + w - 12, arm_y, 16, 12))

    # Big weapon / staff
    if facing_right:
        pygame.draw.rect(surface, ENEMY_BOSS_GOLD,
                         (bx + w, arm_y - 8, 6, 40))
        pygame.draw.polygon(surface, (200, 50, 50), [
            (bx + w + 3, arm_y - 8),
            (bx + w - 4, arm_y - 18),
            (bx + w + 10, arm_y - 18),
        ])
    else:
        pygame.draw.rect(surface, ENEMY_BOSS_GOLD,
                         (bx - 6, arm_y - 8, 6, 40))
        pygame.draw.polygon(surface, (200, 50, 50), [
            (bx - 3, arm_y - 8),
            (bx - 10, arm_y - 18),
            (bx + 4, arm_y - 18),
        ])

    # Legs
    pygame.draw.rect(surface, ENEMY_BOSS_DARK,
                     (bx + 12, by + h * 0.78, 16, h * 0.22))
    pygame.draw.rect(surface, ENEMY_BOSS_DARK,
                     (bx + w - 28, by + h * 0.78, 16, h * 0.22))

    # Phase 2: fire aura
    if phase == 2:
        for i in range(8):
            angle = (anim_frame * 0.15 + i * 0.785)
            fx = head_cx + int(math.cos(angle) * (w * 0.6))
            fy = by + int(h * 0.5) + int(math.sin(angle) * (h * 0.3))
            size = 4 + int(abs(math.sin(angle + anim_frame * 0.2)) * 4)
            pygame.draw.circle(surface, (255, 120, 30), (fx, fy), size)
