"""
Smoothing Module

Provides signal smoothing algorithms for stable tracking.
Reduces jitter in landmark positions and cursor movement.
"""

from __future__ import annotations

from typing import Optional, List, Union
from collections import deque
from dataclasses import dataclass


@dataclass
class SmoothingConfig:
    """Smoothing configuration.
    
    Attributes:
        alpha: EMA smoothing factor (0-1, higher = more responsive)
        window_size: Moving average window size
    """
    alpha: float = 0.4
    window_size: int = 5


class ExponentialMovingAverage:
    """Exponential Moving Average (EMA) smoother.
    
    Applies exponential smoothing to reduce noise in signals.
    Formula: smoothed = alpha * current + (1 - alpha) * previous
    
    Attributes:
        alpha: Smoothing factor (0-1)
            - 0.1-0.3: Very smooth, high latency
            - 0.3-0.5: Balanced smoothing
            - 0.5-0.8: Responsive, some jitter
            - 0.8-1.0: Very responsive, minimal smoothing
    
    Example:
        >>> ema = ExponentialMovingAverage(alpha=0.4)
        >>> values = [1.0, 1.2, 0.9, 1.1, 1.0]
        >>> smoothed = [ema.update(v) for v in values]
    """
    
    def __init__(self, alpha: float = 0.4) -> None:
        """Initialize EMA smoother.
        
        Args:
            alpha: Smoothing factor (0-1)
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("Alpha must be between 0 and 1")
        
        self.alpha = alpha
        self._value: Optional[float] = None
        self._initialized = False
    
    @property
    def value(self) -> Optional[float]:
        """Get current smoothed value."""
        return self._value
    
    @property
    def is_initialized(self) -> bool:
        """Check if smoother has been initialized."""
        return self._initialized
    
    def update(self, new_value: float) -> float:
        """Update with new value and get smoothed result.
        
        Args:
            new_value: New input value
            
        Returns:
            Smoothed value
        """
        if not self._initialized:
            self._value = new_value
            self._initialized = True
        else:
            self._value = self.alpha * new_value + (1 - self.alpha) * self._value
        
        return self._value
    
    def reset(self) -> None:
        """Reset smoother state."""
        self._value = None
        self._initialized = False
    
    def set_alpha(self, alpha: float) -> None:
        """Update smoothing factor.
        
        Args:
            alpha: New smoothing factor (0-1)
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("Alpha must be between 0 and 1")
        self.alpha = alpha


class MovingAverage:
    """Simple Moving Average (SMA) smoother.
    
    Computes the average of the last N values.
    More stable than EMA but with higher latency.
    
    Example:
        >>> ma = MovingAverage(window_size=5)
        >>> values = [1.0, 2.0, 3.0, 4.0, 5.0]
        >>> smoothed = [ma.update(v) for v in values]
        >>> print(smoothed[-1])  # 3.0 (average of all 5)
    """
    
    def __init__(self, window_size: int = 5) -> None:
        """Initialize moving average smoother.
        
        Args:
            window_size: Number of values to average
        """
        if window_size < 1:
            raise ValueError("Window size must be at least 1")
        
        self.window_size = window_size
        self._values: deque = deque(maxlen=window_size)
        self._sum = 0.0
    
    @property
    def value(self) -> Optional[float]:
        """Get current smoothed value."""
        if not self._values:
            return None
        return self._sum / len(self._values)
    
    @property
    def is_full(self) -> bool:
        """Check if window is full."""
        return len(self._values) == self.window_size
    
    def update(self, new_value: float) -> float:
        """Update with new value and get smoothed result.
        
        Args:
            new_value: New input value
            
        Returns:
            Smoothed value (average)
        """
        # Remove oldest value from sum if window is full
        if len(self._values) == self.window_size:
            self._sum -= self._values[0]
        
        self._values.append(new_value)
        self._sum += new_value
        
        return self._sum / len(self._values)
    
    def reset(self) -> None:
        """Reset smoother state."""
        self._values.clear()
        self._sum = 0.0


class DoubleExponentialSmoothing:
    """Double Exponential Smoothing (Holt's method).
    
    Better for tracking data with trends.
    Uses two smoothing factors: alpha for level and beta for trend.
    
    Example:
        >>> des = DoubleExponentialSmoothing(alpha=0.4, beta=0.1)
        >>> for value in data:
        ...     smoothed = des.update(value)
    """
    
    def __init__(self, alpha: float = 0.4, beta: float = 0.1) -> None:
        """Initialize double exponential smoother.
        
        Args:
            alpha: Level smoothing factor (0-1)
            beta: Trend smoothing factor (0-1)
        """
        self.alpha = alpha
        self.beta = beta
        self._level: Optional[float] = None
        self._trend: Optional[float] = None
        self._initialized = False
    
    @property
    def value(self) -> Optional[float]:
        """Get current smoothed value."""
        if self._level is None:
            return None
        return self._level + self._trend if self._trend else self._level
    
    def update(self, new_value: float) -> float:
        """Update with new value and get smoothed result.
        
        Args:
            new_value: New input value
            
        Returns:
            Smoothed value
        """
        if not self._initialized:
            self._level = new_value
            self._trend = 0.0
            self._initialized = True
        else:
            prev_level = self._level
            self._level = self.alpha * new_value + (1 - self.alpha) * (self._level + self._trend)
            self._trend = self.beta * (self._level - prev_level) + (1 - self.beta) * self._trend
        
        return self._level + self._trend
    
    def reset(self) -> None:
        """Reset smoother state."""
        self._level = None
        self._trend = None
        self._initialized = False


class OneEuroFilter:
    """One Euro Filter for low-latency smoothing.
    
    Adaptive filter that adjusts smoothing based on signal velocity.
    Provides low latency during fast movements and high smoothing
    during slow movements.
    
    Reference: https://gery.casiez.net/1euro/
    
    Example:
        >>> filter = OneEuroFilter(min_cutoff=1.0, beta=0.007)
        >>> for value in data:
        ...     smoothed = filter.update(value, timestamp)
    """
    
    def __init__(
        self,
        min_cutoff: float = 1.0,
        beta: float = 0.007,
        d_cutoff: float = 1.0
    ) -> None:
        """Initialize One Euro filter.
        
        Args:
            min_cutoff: Minimum cutoff frequency (higher = less smoothing)
            beta: Speed coefficient (higher = faster adaptation)
            d_cutoff: Derivative cutoff frequency
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self._x_filter: Optional[ExponentialMovingAverage] = None
        self._dx_filter: Optional[ExponentialMovingAverage] = None
        self._last_value: Optional[float] = None
        self._last_time: Optional[float] = None
    
    def _alpha(self, cutoff: float, dt: float) -> float:
        """Calculate alpha from cutoff frequency and time delta."""
        import math
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)
    
    def update(self, value: float, timestamp: float) -> float:
        """Update filter with new value.
        
        Args:
            value: New input value
            timestamp: Current timestamp in seconds
            
        Returns:
            Filtered value
        """
        if self._last_time is None:
            # First update
            self._last_value = value
            self._last_time = timestamp
            self._x_filter = ExponentialMovingAverage(alpha=0.5)
            self._dx_filter = ExponentialMovingAverage(alpha=0.5)
            return value
        
        dt = timestamp - self._last_time
        if dt <= 0:
            return self._last_value
        
        # Estimate derivative
        dx = (value - self._last_value) / dt
        
        # Filter derivative
        d_alpha = self._alpha(self.d_cutoff, dt)
        self._dx_filter.set_alpha(d_alpha)
        dx_hat = self._dx_filter.update(dx)
        
        # Adaptive cutoff based on velocity
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # Filter value
        x_alpha = self._alpha(cutoff, dt)
        self._x_filter.set_alpha(x_alpha)
        x_hat = self._x_filter.update(value)
        
        self._last_value = x_hat
        self._last_time = timestamp
        
        return x_hat
    
    def reset(self) -> None:
        """Reset filter state."""
        self._x_filter = None
        self._dx_filter = None
        self._last_value = None
        self._last_time = None


class Point2DSmoother:
    """Smooths 2D point coordinates.
    
    Applies smoothing independently to X and Y coordinates.
    
    Example:
        >>> smoother = Point2DSmoother(alpha=0.4)
        >>> smoothed_x, smoothed_y = smoother.update(x, y)
    """
    
    def __init__(
        self, 
        alpha: float = 0.4,
        smoother_type: str = "ema"
    ) -> None:
        """Initialize 2D point smoother.
        
        Args:
            alpha: Smoothing factor
            smoother_type: "ema" or "moving_average"
        """
        if smoother_type == "ema":
            self._x_smoother = ExponentialMovingAverage(alpha)
            self._y_smoother = ExponentialMovingAverage(alpha)
        else:
            self._x_smoother = MovingAverage(int(1 / alpha))
            self._y_smoother = MovingAverage(int(1 / alpha))
    
    def update(self, x: float, y: float) -> tuple[float, float]:
        """Update with new coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of smoothed (x, y)
        """
        return (
            self._x_smoother.update(x),
            self._y_smoother.update(y)
        )
    
    def reset(self) -> None:
        """Reset smoother state."""
        self._x_smoother.reset()
        self._y_smoother.reset()


class Point3DSmoother:
    """Smooths 3D point coordinates.
    
    Applies smoothing independently to X, Y, and Z coordinates.
    """
    
    def __init__(self, alpha: float = 0.4) -> None:
        """Initialize 3D point smoother.
        
        Args:
            alpha: Smoothing factor
        """
        self._x_smoother = ExponentialMovingAverage(alpha)
        self._y_smoother = ExponentialMovingAverage(alpha)
        self._z_smoother = ExponentialMovingAverage(alpha)
    
    def update(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        """Update with new coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            
        Returns:
            Tuple of smoothed (x, y, z)
        """
        return (
            self._x_smoother.update(x),
            self._y_smoother.update(y),
            self._z_smoother.update(z)
        )
    
    def reset(self) -> None:
        """Reset smoother state."""
        self._x_smoother.reset()
        self._y_smoother.reset()
        self._z_smoother.reset()
