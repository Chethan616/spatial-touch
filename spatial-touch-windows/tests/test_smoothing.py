"""
Tests for Smoothing Module
"""

import pytest
import math

from spatial_touch.utils.smoothing import (
    ExponentialMovingAverage,
    MovingAverage,
    DoubleExponentialSmoothing,
    OneEuroFilter,
    Point2DSmoother,
    Point3DSmoother,
)


class TestExponentialMovingAverage:
    """Tests for ExponentialMovingAverage class."""
    
    def test_initial_value_is_first_input(self):
        """First input should be returned unchanged."""
        ema = ExponentialMovingAverage(alpha=0.5)
        result = ema.update(10.0)
        assert result == 10.0
    
    def test_smoothing_applied_on_subsequent_inputs(self):
        """Subsequent inputs should be smoothed."""
        ema = ExponentialMovingAverage(alpha=0.5)
        ema.update(10.0)
        result = ema.update(20.0)
        
        # Expected: 0.5 * 20 + 0.5 * 10 = 15
        assert result == 15.0
    
    def test_higher_alpha_more_responsive(self):
        """Higher alpha should give more weight to new values."""
        ema_low = ExponentialMovingAverage(alpha=0.2)
        ema_high = ExponentialMovingAverage(alpha=0.8)
        
        # Initialize with same value
        ema_low.update(0.0)
        ema_high.update(0.0)
        
        # Update with new value
        result_low = ema_low.update(10.0)
        result_high = ema_high.update(10.0)
        
        # High alpha should be closer to new value
        assert result_high > result_low
        assert result_high == 8.0  # 0.8 * 10 + 0.2 * 0
        assert result_low == 2.0   # 0.2 * 10 + 0.8 * 0
    
    def test_reset_clears_state(self):
        """Reset should clear internal state."""
        ema = ExponentialMovingAverage(alpha=0.5)
        ema.update(10.0)
        ema.update(20.0)
        ema.reset()
        
        assert not ema.is_initialized
        assert ema.value is None
    
    def test_invalid_alpha_raises_error(self):
        """Invalid alpha values should raise ValueError."""
        with pytest.raises(ValueError):
            ExponentialMovingAverage(alpha=-0.1)
        
        with pytest.raises(ValueError):
            ExponentialMovingAverage(alpha=1.5)
    
    def test_set_alpha_updates_smoothing(self):
        """set_alpha should update the smoothing factor."""
        ema = ExponentialMovingAverage(alpha=0.5)
        ema.set_alpha(0.8)
        assert ema.alpha == 0.8


class TestMovingAverage:
    """Tests for MovingAverage class."""
    
    def test_single_value(self):
        """Single value should be returned unchanged."""
        ma = MovingAverage(window_size=3)
        result = ma.update(10.0)
        assert result == 10.0
    
    def test_average_of_window(self):
        """Should return average of values in window."""
        ma = MovingAverage(window_size=3)
        ma.update(10.0)
        ma.update(20.0)
        result = ma.update(30.0)
        
        # Average of 10, 20, 30
        assert result == 20.0
    
    def test_sliding_window(self):
        """Old values should be removed when window is full."""
        ma = MovingAverage(window_size=3)
        ma.update(10.0)
        ma.update(20.0)
        ma.update(30.0)
        result = ma.update(40.0)
        
        # Average of 20, 30, 40 (10 removed)
        assert result == 30.0
    
    def test_reset_clears_window(self):
        """Reset should clear the window."""
        ma = MovingAverage(window_size=3)
        ma.update(10.0)
        ma.update(20.0)
        ma.reset()
        
        assert ma.value is None
        assert not ma.is_full


class TestDoubleExponentialSmoothing:
    """Tests for DoubleExponentialSmoothing class."""
    
    def test_handles_linear_trend(self):
        """Should handle data with linear trend."""
        des = DoubleExponentialSmoothing(alpha=0.5, beta=0.5)
        
        # Feed linear sequence
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        results = [des.update(v) for v in values]
        
        # Should track the trend
        assert all(r > 0 for r in results)
        assert results[-1] > results[0]
    
    def test_reset_clears_state(self):
        """Reset should clear internal state."""
        des = DoubleExponentialSmoothing(alpha=0.5, beta=0.5)
        des.update(10.0)
        des.update(20.0)
        des.reset()
        
        assert des.value is None


class TestOneEuroFilter:
    """Tests for OneEuroFilter class."""
    
    def test_first_value_returned_unchanged(self):
        """First value should be returned unchanged."""
        oef = OneEuroFilter(min_cutoff=1.0, beta=0.007)
        result = oef.update(10.0, 0.0)
        assert result == 10.0
    
    def test_smoothing_on_slow_movement(self):
        """Slow movements should be heavily smoothed."""
        oef = OneEuroFilter(min_cutoff=1.0, beta=0.007)
        
        oef.update(0.0, 0.0)
        result = oef.update(1.0, 1.0)  # Slow change over 1 second
        
        # Should be smoothed (closer to 0 than to 1)
        assert 0 < result < 1
    
    def test_reset_clears_state(self):
        """Reset should clear filter state."""
        oef = OneEuroFilter(min_cutoff=1.0, beta=0.007)
        oef.update(10.0, 0.0)
        oef.update(20.0, 1.0)
        oef.reset()
        
        # After reset, first value should be returned unchanged
        result = oef.update(5.0, 0.0)
        assert result == 5.0


class TestPoint2DSmoother:
    """Tests for Point2DSmoother class."""
    
    def test_smooths_both_coordinates(self):
        """Should smooth both X and Y coordinates."""
        smoother = Point2DSmoother(alpha=0.5)
        
        x, y = smoother.update(0.0, 0.0)
        assert x == 0.0
        assert y == 0.0
        
        x, y = smoother.update(10.0, 20.0)
        assert x == 5.0   # 0.5 * 10 + 0.5 * 0
        assert y == 10.0  # 0.5 * 20 + 0.5 * 0
    
    def test_reset_clears_both_smoothers(self):
        """Reset should clear both X and Y smoothers."""
        smoother = Point2DSmoother(alpha=0.5)
        smoother.update(10.0, 20.0)
        smoother.reset()
        
        # After reset, should return input unchanged
        x, y = smoother.update(5.0, 15.0)
        assert x == 5.0
        assert y == 15.0


class TestPoint3DSmoother:
    """Tests for Point3DSmoother class."""
    
    def test_smooths_all_coordinates(self):
        """Should smooth X, Y, and Z coordinates."""
        smoother = Point3DSmoother(alpha=0.5)
        
        x, y, z = smoother.update(0.0, 0.0, 0.0)
        assert x == 0.0
        assert y == 0.0
        assert z == 0.0
        
        x, y, z = smoother.update(10.0, 20.0, 30.0)
        assert x == 5.0
        assert y == 10.0
        assert z == 15.0


class TestSmoothingPerformance:
    """Performance-related tests for smoothing algorithms."""
    
    def test_ema_with_noise(self):
        """EMA should reduce noise in signal."""
        import random
        random.seed(42)
        
        ema = ExponentialMovingAverage(alpha=0.2)
        
        # Generate noisy signal around 10
        noisy_values = [10 + random.gauss(0, 2) for _ in range(100)]
        smoothed_values = [ema.update(v) for v in noisy_values]
        
        # Calculate variance
        mean_noisy = sum(noisy_values) / len(noisy_values)
        mean_smoothed = sum(smoothed_values) / len(smoothed_values)
        
        var_noisy = sum((v - mean_noisy) ** 2 for v in noisy_values) / len(noisy_values)
        var_smoothed = sum((v - mean_smoothed) ** 2 for v in smoothed_values) / len(smoothed_values)
        
        # Smoothed signal should have lower variance
        assert var_smoothed < var_noisy
    
    def test_ma_with_noise(self):
        """Moving average should reduce noise in signal."""
        import random
        random.seed(42)
        
        ma = MovingAverage(window_size=5)
        
        # Generate noisy signal around 10
        noisy_values = [10 + random.gauss(0, 2) for _ in range(100)]
        smoothed_values = [ma.update(v) for v in noisy_values]
        
        # Calculate variance (skip first few values for MA to stabilize)
        skip = 10
        mean_noisy = sum(noisy_values[skip:]) / len(noisy_values[skip:])
        mean_smoothed = sum(smoothed_values[skip:]) / len(smoothed_values[skip:])
        
        var_noisy = sum((v - mean_noisy) ** 2 for v in noisy_values[skip:]) / len(noisy_values[skip:])
        var_smoothed = sum((v - mean_smoothed) ** 2 for v in smoothed_values[skip:]) / len(smoothed_values[skip:])
        
        # Smoothed signal should have lower variance
        assert var_smoothed < var_noisy
