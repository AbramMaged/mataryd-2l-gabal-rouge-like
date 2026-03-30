"""
collision.py — Collision detection for platforms, walls, and entities.
"""
import pygame


def aabb_collision(rect1, rect2):
    """Basic AABB collision between two pygame.Rect."""
    return rect1.colliderect(rect2)


def check_platform_collision(entity_rect, entity_vel_y, platforms):
    """
    Check one-way platform collision (only from above).
    Returns (landed, new_y, platform) or (False, None, None).
    """
    if entity_vel_y < 0:
        return False, None, None

    for plat in platforms:
        plat_rect = plat.rect
        # Check if entity is falling onto platform from above
        if (entity_rect.bottom >= plat_rect.top and
            entity_rect.bottom <= plat_rect.top + entity_vel_y + 8 and
            entity_rect.right > plat_rect.left + 4 and
            entity_rect.left < plat_rect.right - 4):
            return True, plat_rect.top - entity_rect.height, plat
    return False, None, None


def check_wall_collision(entity_rect, walls):
    """
    Check if entity is touching or very near a wall (within 6px).
    Uses proximity so the player can wall-jump even when clamped
    at the level boundary.
    Returns: 'left', 'right', or None
    """
    # Inflate rect slightly for proximity detection
    check_rect = entity_rect.inflate(12, 0)
    for wall in walls:
        if check_rect.colliderect(wall.rect):
            # Make sure it's actually a side contact, not standing on top
            if entity_rect.bottom > wall.rect.top + 10:
                if entity_rect.centerx < wall.rect.centerx:
                    return 'right'   # wall is to entity's right
                else:
                    return 'left'    # wall is to entity's left
    return None


def check_ground_collision(entity_rect, entity_vel_y, ground_y):
    """Check if entity has hit the ground."""
    if entity_vel_y >= 0 and entity_rect.bottom >= ground_y:
        return True, ground_y - entity_rect.height
    return False, None


def rect_contains_point(rect, point):
    """Check if a point is inside a rect."""
    return rect.collidepoint(point)


def circles_collide(x1, y1, r1, x2, y2, r2):
    """Circle-circle collision."""
    dx = x2 - x1
    dy = y2 - y1
    dist_sq = dx * dx + dy * dy
    radius_sum = r1 + r2
    return dist_sq <= radius_sum * radius_sum
