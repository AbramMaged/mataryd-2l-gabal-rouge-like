"""
animations.py — Animation state machine for entities.
"""


class AnimationState:
    IDLE = "idle"
    RUN = "run"
    JUMP = "jump"
    FALL = "fall"
    CROUCH = "crouch"
    DASH = "dash"
    SHOOT = "shoot"
    HURT = "hurt"
    DIE = "die"
    WALL_SLIDE = "wall_slide"
    # Enemy specific
    ATTACK = "attack"
    CHARGE = "charge"
    COOLDOWN = "cooldown"
    TELEGRAPH = "telegraph"
    # Boss specific
    SLAM = "slam"
    PHASE_CHANGE = "phase_change"


class Animator:
    """Simple frame-based animator."""

    def __init__(self, frame_durations=None):
        """
        frame_durations: dict of state -> frames_per_animation_frame
        """
        self.state = AnimationState.IDLE
        self.frame = 0
        self.timer = 0
        self.frame_durations = frame_durations or {
            AnimationState.IDLE: 20,
            AnimationState.RUN: 6,
            AnimationState.JUMP: 1,
            AnimationState.FALL: 1,
            AnimationState.CROUCH: 1,
            AnimationState.DASH: 3,
            AnimationState.SHOOT: 4,
            AnimationState.HURT: 5,
            AnimationState.DIE: 8,
            AnimationState.WALL_SLIDE: 8,
            AnimationState.ATTACK: 6,
            AnimationState.CHARGE: 4,
            AnimationState.COOLDOWN: 10,
            AnimationState.TELEGRAPH: 8,
            AnimationState.SLAM: 5,
            AnimationState.PHASE_CHANGE: 4,
        }
        self.max_frames = {
            AnimationState.IDLE: 4,
            AnimationState.RUN: 6,
            AnimationState.JUMP: 2,
            AnimationState.FALL: 2,
            AnimationState.CROUCH: 1,
            AnimationState.DASH: 3,
            AnimationState.SHOOT: 3,
            AnimationState.HURT: 2,
            AnimationState.DIE: 4,
            AnimationState.WALL_SLIDE: 2,
            AnimationState.ATTACK: 4,
            AnimationState.CHARGE: 4,
            AnimationState.COOLDOWN: 2,
            AnimationState.TELEGRAPH: 3,
            AnimationState.SLAM: 4,
            AnimationState.PHASE_CHANGE: 6,
        }

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame = 0
            self.timer = 0

    def update(self):
        self.timer += 1
        duration = self.frame_durations.get(self.state, 10)
        if self.timer >= duration:
            self.timer = 0
            max_f = self.max_frames.get(self.state, 4)
            self.frame = (self.frame + 1) % max_f

    def get_frame(self):
        return self.frame
