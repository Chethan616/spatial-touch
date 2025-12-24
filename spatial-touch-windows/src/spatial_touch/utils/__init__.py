"""Utility modules for Spatial Touch."""

from spatial_touch.utils.smoothing import ExponentialMovingAverage, MovingAverage
from spatial_touch.utils.logger import setup_logging, get_logger
from spatial_touch.utils.math_helpers import euclidean_distance, normalize_to_range

__all__ = [
    "ExponentialMovingAverage",
    "MovingAverage",
    "setup_logging",
    "get_logger",
    "euclidean_distance",
    "normalize_to_range",
]
