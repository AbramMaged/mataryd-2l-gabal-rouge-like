"""
upgrade_system.py — Post-wave upgrade selection.
Player picks 1 of 3 random upgrades after each wave.
"""
import random


# All possible upgrades
UPGRADE_POOL = [
    {
        "id": "extra_stamina",
        "name": "Extra Stamina",
        "description": "+1 stamina bar for dashing",
        "icon": "stamina",
        "max_stacks": 4,
        "apply": lambda player: _add_stamina(player),
    },
    {
        "id": "stamina_recovery",
        "name": "Quick Recovery",
        "description": "Stamina recharges faster",
        "icon": "stamina",
        "max_stacks": 5,
        "apply": lambda player: _faster_stamina(player),
    },
    {
        "id": "dash_shield",
        "name": "Dash Shield",
        "description": "Dash i-frames last longer",
        "icon": "shield",
        "max_stacks": 3,
        "apply": lambda player: _extend_dash_iframes(player),
    },
    {
        "id": "shotgun_spread",
        "name": "Wider Spread",
        "description": "+2 shotgun pellets",
        "icon": "shotgun",
        "max_stacks": 4,
        "apply": lambda player: _add_pellets(player),
    },
    {
        "id": "shotgun_damage",
        "name": "Heavy Load",
        "description": "Shotgun pellets hit harder",
        "icon": "shotgun",
        "max_stacks": 5,
        "apply": lambda player: _shotgun_damage(player),
    },
    {
        "id": "shotgun_ammo",
        "name": "Extra Shells",
        "description": "+2 shells before reload",
        "icon": "shotgun",
        "max_stacks": 4,
        "apply": lambda player: _add_shells(player),
    },
    {
        "id": "deagle_damage",
        "name": "Deagle Power",
        "description": "Deagle hits harder",
        "icon": "deagle",
        "max_stacks": 5,
        "apply": lambda player: _deagle_damage(player),
    },
    {
        "id": "deagle_piercing",
        "name": "Piercing Rounds",
        "description": "Deagle bullets pierce 1 enemy",
        "icon": "deagle",
        "max_stacks": 1,
        "apply": lambda player: _deagle_piercing(player),
    },
    {
        "id": "deagle_ammo",
        "name": "Extended Mag",
        "description": "+3 bullets before reload",
        "icon": "deagle",
        "max_stacks": 4,
        "apply": lambda player: _add_bullets(player),
    },
    {
        "id": "max_hp",
        "name": "Extra Heart",
        "description": "+1 max heart card",
        "icon": "heart",
        "max_stacks": 5,
        "apply": lambda player: _add_heart(player),
    },
    {
        "id": "heal",
        "name": "Healing",
        "description": "Restore 2 hearts",
        "icon": "heart",
        "max_stacks": 99,
        "apply": lambda player: _heal(player),
    },
    {
        "id": "move_speed",
        "name": "Swift Feet",
        "description": "Move faster",
        "icon": "speed",
        "max_stacks": 4,
        "apply": lambda player: _speed_up(player),
    },
]


class UpgradeSystem:
    """Manages upgrade offering and application."""

    def __init__(self):
        self.upgrade_counts = {}  # id -> times taken
        self.offered_upgrades = []
        self.selection_made = False
        self.picks_allowed = 1

    def offer_upgrades(self):
        """Generate 3 random upgrade choices."""
        available = []
        for up in UPGRADE_POOL:
            count = self.upgrade_counts.get(up["id"], 0)
            if count < up["max_stacks"]:
                available.append(up)

        if len(available) <= 3:
            self.offered_upgrades = available[:]
        else:
            self.offered_upgrades = random.sample(available, 3)

        self.selection_made = False
        return self.offered_upgrades

    def select_upgrade(self, index, player):
        """Apply the selected upgrade to the player."""
        if index < 0 or index >= len(self.offered_upgrades):
            return None

        # Pop so it can't be chosen again if picks_allowed > 1
        upgrade = self.offered_upgrades.pop(index)
        upgrade["apply"](player)

        uid = upgrade["id"]
        self.upgrade_counts[uid] = self.upgrade_counts.get(uid, 0) + 1
        self.selection_made = True
        return upgrade

    def reset(self):
        """Reset all upgrades (new game)."""
        self.upgrade_counts = {}
        self.offered_upgrades = []
        self.selection_made = False


# ─── Upgrade effect functions ─────────────────────────────

def _add_stamina(player):
    from core.settings import MAX_STAMINA
    if player.max_stamina < MAX_STAMINA:
        player.max_stamina += 1
        player.stamina = player.max_stamina


def _faster_stamina(player):
    player.stamina_recharge_rate = max(10, player.stamina_recharge_rate - 5)


def _extend_dash_iframes(player):
    # Increase dash i-frames globally (hacky but works)
    from core import settings
    settings.DASH_IFRAMES += 4


def _add_pellets(player):
    player.shotgun.extra_pellets += 2


def _shotgun_damage(player):
    player.shotgun.damage_mult += 0.2


def _add_shells(player):
    player.shotgun.ammo_bonus += 2
    player.shotgun.current_ammo = player.shotgun.get_max_ammo()


def _deagle_damage(player):
    player.deagle.damage_mult += 0.25


def _deagle_piercing(player):
    player.deagle.piercing = True


def _add_bullets(player):
    player.deagle.ammo_bonus += 3
    player.deagle.current_ammo = player.deagle.get_max_ammo()


def _add_heart(player):
    player.max_hearts += 1
    player.hearts += 1
    player.heart_flip_timers.append(0)


def _heal(player):
    player.heal(2)


def _speed_up(player):
    player.speed_mult += 0.15
