"""
Math Helpers Module

Provides mathematical utility functions for gesture detection.
"""

from __future__ import annotations

import math
from typing import Tuple, Sequence, Union

# Type aliases
Point2D = Tuple[float, float]
Point3D = Tuple[float, float, float]
PointND = Sequence[float]


def euclidean_distance(point_a: PointND, point_b: PointND) -> float:
    """Calculate Euclidean distance between two points.
    
    Works with 2D, 3D, or N-dimensional points.
    
    Args:
        point_a: First point coordinates
        point_b: Second point coordinates
        
    Returns:
        Euclidean distance
        
    Example:
        >>> euclidean_distance((0, 0), (3, 4))
        5.0
        >>> euclidean_distance((0, 0, 0), (1, 1, 1))
        1.732...
    """
    if len(point_a) != len(point_b):
        raise ValueError("Points must have same dimensions")
    
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


def euclidean_distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate 2D Euclidean distance (optimized).
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
        
    Returns:
        Euclidean distance
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def euclidean_distance_3d(
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float
) -> float:
    """Calculate 3D Euclidean distance (optimized).
    
    Args:
        x1, y1, z1: First point coordinates
        x2, y2, z2: Second point coordinates
        
    Returns:
        Euclidean distance
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def manhattan_distance(point_a: PointND, point_b: PointND) -> float:
    """Calculate Manhattan (L1) distance between two points.
    
    Args:
        point_a: First point coordinates
        point_b: Second point coordinates
        
    Returns:
        Manhattan distance
    """
    return sum(abs(a - b) for a, b in zip(point_a, point_b))


def normalize_to_range(
    value: float,
    old_min: float,
    old_max: float,
    new_min: float = 0.0,
    new_max: float = 1.0
) -> float:
    """Normalize a value from one range to another.
    
    Args:
        value: Value to normalize
        old_min: Original minimum
        old_max: Original maximum
        new_min: Target minimum
        new_max: Target maximum
        
    Returns:
        Normalized value
        
    Example:
        >>> normalize_to_range(50, 0, 100, 0, 1)
        0.5
    """
    if old_max == old_min:
        return new_min
    
    normalized = (value - old_min) / (old_max - old_min)
    return new_min + normalized * (new_max - new_min)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to a range.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0-1)
        
    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def inverse_lerp(a: float, b: float, value: float) -> float:
    """Find interpolation factor for a value between a and b.
    
    Args:
        a: Start value
        b: End value
        value: Value between a and b
        
    Returns:
        Interpolation factor (0-1)
    """
    if b == a:
        return 0.0
    return (value - a) / (b - a)


def angle_between_points(p1: Point2D, p2: Point2D) -> float:
    """Calculate angle between two 2D points.
    
    Args:
        p1: First point (x, y)
        p2: Second point (x, y)
        
    Returns:
        Angle in radians
    """
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def angle_between_points_degrees(p1: Point2D, p2: Point2D) -> float:
    """Calculate angle between two 2D points in degrees.
    
    Args:
        p1: First point (x, y)
        p2: Second point (x, y)
        
    Returns:
        Angle in degrees
    """
    return math.degrees(angle_between_points(p1, p2))


def midpoint(p1: PointND, p2: PointND) -> tuple:
    """Calculate midpoint between two points.
    
    Args:
        p1: First point
        p2: Second point
        
    Returns:
        Midpoint coordinates
    """
    return tuple((a + b) / 2 for a, b in zip(p1, p2))


def velocity(
    p1: Point2D, 
    p2: Point2D, 
    dt: float
) -> Tuple[float, float]:
    """Calculate velocity between two positions.
    
    Args:
        p1: Previous position
        p2: Current position
        dt: Time delta in seconds
        
    Returns:
        Velocity as (vx, vy)
    """
    if dt <= 0:
        return (0.0, 0.0)
    
    return (
        (p2[0] - p1[0]) / dt,
        (p2[1] - p1[1]) / dt
    )


def velocity_magnitude(p1: Point2D, p2: Point2D, dt: float) -> float:
    """Calculate velocity magnitude.
    
    Args:
        p1: Previous position
        p2: Current position
        dt: Time delta in seconds
        
    Returns:
        Velocity magnitude
    """
    vx, vy = velocity(p1, p2, dt)
    return math.sqrt(vx ** 2 + vy ** 2)


def smooth_step(edge0: float, edge1: float, x: float) -> float:
    """Smooth step interpolation (Hermite).
    
    Args:
        edge0: Lower edge
        edge1: Upper edge
        x: Input value
        
    Returns:
        Smoothly interpolated value (0-1)
    """
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * (3 - 2 * x)


def smoother_step(edge0: float, edge1: float, x: float) -> float:
    """Smoother step interpolation (Ken Perlin's version).
    
    Args:
        edge0: Lower edge
        edge1: Upper edge
        x: Input value
        
    Returns:
        Smoothly interpolated value (0-1)
    """
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)


def is_point_in_rect(
    point: Point2D,
    rect_x: float,
    rect_y: float,
    rect_w: float,
    rect_h: float
) -> bool:
    """Check if point is inside rectangle.
    
    Args:
        point: Point (x, y)
        rect_x: Rectangle left edge
        rect_y: Rectangle top edge
        rect_w: Rectangle width
        rect_h: Rectangle height
        
    Returns:
        True if point is inside rectangle
    """
    return (
        rect_x <= point[0] <= rect_x + rect_w and
        rect_y <= point[1] <= rect_y + rect_h
    )


def rotate_point(
    point: Point2D, 
    angle: float, 
    center: Point2D = (0.0, 0.0)
) -> Point2D:
    """Rotate a point around a center.
    
    Args:
        point: Point to rotate (x, y)
        angle: Rotation angle in radians
        center: Center of rotation
        
    Returns:
        Rotated point (x, y)
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate to origin
    x = point[0] - center[0]
    y = point[1] - center[1]
    
    # Rotate
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    # Translate back
    return (new_x + center[0], new_y + center[1])


def vector_magnitude(v: PointND) -> float:
    """Calculate vector magnitude.
    
    Args:
        v: Vector components
        
    Returns:
        Magnitude
    """
    return math.sqrt(sum(x ** 2 for x in v))


def normalize_vector(v: PointND) -> tuple:
    """Normalize a vector to unit length.
    
    Args:
        v: Vector to normalize
        
    Returns:
        Normalized vector
    """
    mag = vector_magnitude(v)
    if mag == 0:
        return tuple(0.0 for _ in v)
    return tuple(x / mag for x in v)


def dot_product(v1: PointND, v2: PointND) -> float:
    """Calculate dot product of two vectors.
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Dot product
    """
    return sum(a * b for a, b in zip(v1, v2))


def cross_product_2d(v1: Point2D, v2: Point2D) -> float:
    """Calculate 2D cross product (z-component).
    
    Args:
        v1: First vector (x, y)
        v2: Second vector (x, y)
        
    Returns:
        Z-component of cross product
    """
    return v1[0] * v2[1] - v1[1] * v2[0]
