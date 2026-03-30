"""
settings.py — All configurable game constants.
Change values here to tweak gameplay, physics, visuals, controls, etc.
"""
import pygame

# ─── DISPLAY ──────────────────────────────────────────────
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = False
TITLE = "Egyptian Farmer — Roguelike"

# ─── PHYSICS ──────────────────────────────────────────────
GRAVITY = 0.8
TERMINAL_VELOCITY = 18
GROUND_FRICTION = 0.85
AIR_FRICTION = 0.92

# ─── PLAYER ───────────────────────────────────────────────
PLAYER_SPEED = 5.5
PLAYER_ACCEL = 0.9
PLAYER_WIDTH = 36
PLAYER_HEIGHT = 56
PLAYER_CROUCH_HEIGHT = 36
PLAYER_JUMP_FORCE = -17
PLAYER_WALL_JUMP_FORCE_X = 12
PLAYER_WALL_JUMP_FORCE_Y = -15
PLAYER_MAX_HEARTS = 5
PLAYER_COYOTE_TIME = 6  # frames

# ─── DASH ─────────────────────────────────────────────────
DASH_SPEED = 18
DASH_DURATION = 8        # frames
DASH_COOLDOWN = 30       # frames per stamina bar recharge
DASH_IFRAMES = 10        # invincibility frames during dash
STARTING_STAMINA = 2     # stamina bars player starts with
MAX_STAMINA = 6          # max possible stamina bars

# ─── WEAPONS ──────────────────────────────────────────────
# Deagle
DEAGLE_DAMAGE = 35
DEAGLE_FIRE_RATE = 12     # frames between shots
DEAGLE_RELOAD_TIME = 45   # frames to reload
DEAGLE_AMMO_CAPACITY = 7
DEAGLE_BULLET_SPEED = 22
DEAGLE_BULLET_SIZE = 4

# Shotgun
SHOTGUN_DAMAGE = 18        # per pellet
SHOTGUN_PELLETS = 6
SHOTGUN_SPREAD = 10        # degrees total spread
SHOTGUN_FIRE_RATE = 45     # frames between shots (pump delay)
SHOTGUN_RELOAD_TIME = 80   # frames to reload
SHOTGUN_AMMO_CAPACITY = 4
SHOTGUN_PELLET_SPEED = 18
SHOTGUN_PELLET_SIZE = 3

# ─── ENEMIES ─────────────────────────────────────────────
# Grunt
GRUNT_HP = 60
GRUNT_SPEED = 2.0
GRUNT_DAMAGE = 10
GRUNT_FIRE_RATE = 60       # frames between shots
GRUNT_BULLET_SPEED = 5
GRUNT_WIDTH = 32
GRUNT_HEIGHT = 48

# Runner
RUNNER_HP = 35
RUNNER_SPEED = 5.0
RUNNER_DAMAGE = 15
RUNNER_ATTACK_RANGE = 40
RUNNER_WIDTH = 28
RUNNER_HEIGHT = 44

# Heavy
HEAVY_HP = 200
HEAVY_SPEED = 1.2
HEAVY_DAMAGE = 30
HEAVY_FIRE_RATE = 120      # frames between attacks
HEAVY_COOLDOWN = 90        # frames of vulnerability after attack
HEAVY_BULLET_SPEED = 4
HEAVY_WIDTH = 52
HEAVY_HEIGHT = 64

# Boss
BOSS_BASE_HP = 500
BOSS_SPEED = 2.5
BOSS_DAMAGE = 25
BOSS_WIDTH = 80
BOSS_HEIGHT = 96
BOSS_PHASE2_HP_RATIO = 0.5
BOSS_HP_SCALE_PER_CYCLE = 1.5  # multiplier each boss fight

# ─── WAVES ────────────────────────────────────────────────
BOSS_WAVE_INTERVAL = 10
WAVE_ENEMY_BASE_COUNT = 4
WAVE_ENEMY_SCALE = 1.5     # multiply enemy count each wave
WAVE_STAT_SCALE = 0.08     # % increase in enemy stats per wave

# ─── AUDIO ────────────────────────────────────────────────
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.5

# ─── CONTROLS (remappable) ───────────────────────────────
KEYBINDS = {
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "jump": pygame.K_w,
    "jump_alt": pygame.K_SPACE,
    "crouch": pygame.K_s,
    "dash": pygame.K_LSHIFT,
    "parry": pygame.K_f,
    "weapon_1": pygame.K_1,
    "weapon_2": pygame.K_2,
    "switch_weapon": pygame.K_q,
    "reload": pygame.K_r,
    "pause": pygame.K_ESCAPE,
}

# ─── SCREEN SHAKE ─────────────────────────────────────────
SCREEN_SHAKE_INTENSITY = 1.0  # multiplier (0 = off, 1 = normal, 2 = heavy)

# ─── PARTICLES ────────────────────────────────────────────
MAX_PARTICLES = 500
PARTICLE_GRAVITY = 0.3
