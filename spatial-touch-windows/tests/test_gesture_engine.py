"""
Tests for Gesture Engine Module
"""

import pytest
from unittest.mock import MagicMock
import time

from spatial_touch.core.gesture_engine import (
    GestureEngine,
    GestureConfig,
    GestureType,
    GestureState,
    PinchDetector,
    Gesture,
)
from spatial_touch.core.hand_tracker import HandData, Point3D


class TestPinchDetector:
    """Tests for PinchDetector class."""
    
    @pytest.fixture
    def detector(self) -> PinchDetector:
        """Create a pinch detector with default settings."""
        return PinchDetector(threshold=0.05, debounce_ms=0, hold_ms=100)
    
    def test_initial_state_is_idle(self, detector: PinchDetector):
        """Detector should start in IDLE state."""
        assert detector.state == GestureState.IDLE
        assert not detector.is_pinched
    
    def test_pinch_detected_when_distance_below_threshold(self, detector: PinchDetector):
        """Pinch should be detected when distance is below threshold."""
        state = detector.update(0.03)  # Below threshold of 0.05
        assert detector.is_pinched
        assert state == GestureState.TRIGGERED
    
    def test_no_pinch_when_distance_above_threshold(self, detector: PinchDetector):
        """No pinch when distance is above threshold."""
        state = detector.update(0.10)  # Above threshold
        assert not detector.is_pinched
        assert state == GestureState.IDLE
    
    def test_state_transitions_to_released_on_release(self, detector: PinchDetector):
        """State should transition to RELEASED when pinch is released."""
        # Start pinch
        detector.update(0.03)
        assert detector.state == GestureState.TRIGGERED
        
        # Release
        state = detector.update(0.10)
        assert state == GestureState.RELEASED
    
    def test_holding_state_after_hold_time(self, detector: PinchDetector):
        """State should transition to HOLDING after hold time."""
        # Start pinch
        detector.update(0.03)
        
        # Wait and update again (simulating hold)
        time.sleep(0.15)  # Wait longer than hold_ms (100ms)
        state = detector.update(0.03)
        
        assert state == GestureState.HOLDING
    
    def test_reset_clears_state(self, detector: PinchDetector):
        """Reset should clear all state."""
        detector.update(0.03)
        detector.reset()
        
        assert detector.state == GestureState.IDLE
        assert not detector.is_pinched


class TestGestureEngine:
    """Tests for GestureEngine class."""
    
    @pytest.fixture
    def engine(self) -> GestureEngine:
        """Create a gesture engine with default config."""
        config = GestureConfig(
            pinch_threshold=0.05,
            debounce_ms=0,
            hold_time_ms=100,
        )
        return GestureEngine(config)
    
    @pytest.fixture
    def mock_hand_data(self) -> HandData:
        """Create mock hand data with fingers apart."""
        landmarks = [Point3D(0.0, 0.0, 0.0) for _ in range(21)]
        # Set thumb tip at (0.5, 0.5, 0)
        landmarks[4] = Point3D(0.5, 0.5, 0.0)
        # Set index tip at (0.6, 0.5, 0) - far from thumb
        landmarks[8] = Point3D(0.6, 0.5, 0.0)
        # Set middle tip at (0.7, 0.5, 0)
        landmarks[12] = Point3D(0.7, 0.5, 0.0)
        
        return HandData(
            landmarks=landmarks,
            handedness="Right",
            confidence=0.9,
            is_valid=True
        )
    
    @pytest.fixture
    def pinching_hand_data(self) -> HandData:
        """Create mock hand data with pinch gesture."""
        landmarks = [Point3D(0.0, 0.0, 0.0) for _ in range(21)]
        # Set thumb tip and index tip very close
        landmarks[4] = Point3D(0.5, 0.5, 0.0)  # Thumb
        landmarks[8] = Point3D(0.52, 0.5, 0.0)  # Index - close to thumb
        landmarks[12] = Point3D(0.7, 0.5, 0.0)  # Middle
        
        return HandData(
            landmarks=landmarks,
            handedness="Right",
            confidence=0.9,
            is_valid=True
        )
    
    def test_no_gesture_with_invalid_hand(self, engine: GestureEngine):
        """No gestures should be detected with invalid hand data."""
        invalid_hand = HandData(is_valid=False)
        gestures = engine.process(invalid_hand)
        assert len(gestures) == 0
    
    def test_cursor_move_detected(self, engine: GestureEngine, mock_hand_data: HandData):
        """Cursor move should be detected on position change."""
        # First call to establish position
        engine.process(mock_hand_data)
        
        # Move index finger
        mock_hand_data.landmarks[8] = Point3D(0.65, 0.55, 0.0)
        gestures = engine.process(mock_hand_data)
        
        cursor_moves = [g for g in gestures if g.type == GestureType.CURSOR_MOVE]
        assert len(cursor_moves) > 0
    
    def test_left_click_on_pinch(self, engine: GestureEngine, pinching_hand_data: HandData):
        """Left click should be detected on thumb-index pinch."""
        # Start with non-pinching to ensure clean state
        normal_hand = HandData(
            landmarks=[Point3D(0.0, 0.0, 0.0) for _ in range(21)],
            is_valid=True
        )
        normal_hand.landmarks[4] = Point3D(0.5, 0.5, 0.0)
        normal_hand.landmarks[8] = Point3D(0.7, 0.5, 0.0)
        normal_hand.landmarks[12] = Point3D(0.8, 0.5, 0.0)
        
        engine.process(normal_hand)
        
        # Now pinch
        engine.process(pinching_hand_data)
        
        # Release
        gestures = engine.process(normal_hand)
        
        left_clicks = [g for g in gestures if g.type == GestureType.LEFT_CLICK]
        assert len(left_clicks) > 0
    
    def test_callback_triggered_on_gesture(self, engine: GestureEngine, pinching_hand_data: HandData):
        """Registered callbacks should be triggered on gesture."""
        callback_called = []
        
        def on_gesture(gesture: Gesture):
            callback_called.append(gesture.type)
        
        engine.on_gesture(GestureType.LEFT_CLICK, on_gesture)
        
        # Trigger pinch cycle
        normal_hand = HandData(
            landmarks=[Point3D(0.0, 0.0, 0.0) for _ in range(21)],
            is_valid=True
        )
        normal_hand.landmarks[4] = Point3D(0.5, 0.5, 0.0)
        normal_hand.landmarks[8] = Point3D(0.7, 0.5, 0.0)
        normal_hand.landmarks[12] = Point3D(0.8, 0.5, 0.0)
        
        engine.process(normal_hand)
        engine.process(pinching_hand_data)
        engine.process(normal_hand)
        
        assert GestureType.LEFT_CLICK in callback_called
    
    def test_reset_clears_state(self, engine: GestureEngine, pinching_hand_data: HandData):
        """Reset should clear engine state."""
        engine.process(pinching_hand_data)
        engine.reset()
        
        assert engine._last_position is None
        assert not engine._is_dragging


class TestGestureIntegration:
    """Integration tests for gesture detection."""
    
    def test_drag_sequence(self):
        """Test complete drag and drop sequence."""
        config = GestureConfig(
            pinch_threshold=0.05,
            debounce_ms=0,
            hold_time_ms=50,  # Short for testing
        )
        engine = GestureEngine(config)
        
        # Create hands
        def create_hand(thumb_x, index_x):
            landmarks = [Point3D(0.0, 0.0, 0.0) for _ in range(21)]
            landmarks[4] = Point3D(thumb_x, 0.5, 0.0)
            landmarks[8] = Point3D(index_x, 0.5, 0.0)
            landmarks[12] = Point3D(0.8, 0.5, 0.0)
            return HandData(landmarks=landmarks, is_valid=True)
        
        # Open hand
        engine.process(create_hand(0.5, 0.7))
        
        # Start pinch
        engine.process(create_hand(0.5, 0.52))
        
        # Hold (wait for hold time)
        time.sleep(0.1)
        gestures = engine.process(create_hand(0.5, 0.52))
        
        drag_starts = [g for g in gestures if g.type == GestureType.DRAG_START]
        assert len(drag_starts) > 0
        
        # Move while holding
        gestures = engine.process(create_hand(0.6, 0.62))
        drag_moves = [g for g in gestures if g.type == GestureType.DRAG_MOVE]
        assert len(drag_moves) > 0
        
        # Release
        gestures = engine.process(create_hand(0.6, 0.8))
        drag_ends = [g for g in gestures if g.type == GestureType.DRAG_END]
        assert len(drag_ends) > 0
