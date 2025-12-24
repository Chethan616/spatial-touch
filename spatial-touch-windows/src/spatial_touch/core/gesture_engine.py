"""
Gesture Engine Module

Detects and tracks hand gestures from landmark data.
Uses state machines and temporal logic for accurate gesture recognition.
"""

from __future__ import annotations

import time
import logging
from typing import Optional, Callable, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum, auto

from spatial_touch.core.hand_tracker import HandData, Point3D, HandLandmark

logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Supported gesture types."""
    NONE = auto()
    CURSOR_MOVE = auto()
    LEFT_CLICK = auto()
    RIGHT_CLICK = auto()
    DRAG_START = auto()
    DRAG_MOVE = auto()
    DRAG_END = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()


class GestureState(Enum):
    """Gesture state machine states."""
    IDLE = auto()
    TRIGGERED = auto()
    HOLDING = auto()
    RELEASED = auto()


@dataclass
class Gesture:
    """Detected gesture data.
    
    Attributes:
        type: Type of gesture detected
        position: Cursor position (normalized 0-1)
        confidence: Detection confidence
        timestamp: When gesture was detected
        metadata: Additional gesture-specific data
    """
    type: GestureType
    position: tuple[float, float] = (0.0, 0.0)
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GestureConfig:
    """Gesture detection configuration.
    
    Attributes:
        pinch_threshold: Distance threshold for pinch (normalized)
        debounce_ms: Minimum time between gestures
        hold_time_ms: Time to trigger hold gesture
        click_release_ms: Max time for click (vs hold)
        velocity_threshold: Movement velocity threshold
    """
    pinch_threshold: float = 0.05
    debounce_ms: int = 200
    hold_time_ms: int = 300
    click_release_ms: int = 200
    velocity_threshold: float = 0.01
    
    @classmethod
    def from_dict(cls, data: dict) -> GestureConfig:
        """Create config from dictionary."""
        return cls(
            pinch_threshold=data.get("pinch_threshold", 0.05),
            debounce_ms=data.get("debounce_ms", 200),
            hold_time_ms=data.get("hold_time_ms", 300),
            click_release_ms=data.get("click_release_ms", 200),
            velocity_threshold=data.get("velocity_threshold", 0.01),
        )


class PinchDetector:
    """Detects pinch gestures between fingers.
    
    Implements a state machine for accurate pinch detection
    with debouncing and hold detection.
    """
    
    def __init__(
        self, 
        threshold: float = 0.05,
        debounce_ms: int = 200,
        hold_ms: int = 300
    ) -> None:
        """Initialize pinch detector.
        
        Args:
            threshold: Distance threshold for pinch
            debounce_ms: Debounce time in milliseconds
            hold_ms: Hold time threshold in milliseconds
        """
        self.threshold = threshold
        self.debounce_ms = debounce_ms
        self.hold_ms = hold_ms
        
        self._state = GestureState.IDLE
        self._pinch_start_time: Optional[float] = None
        self._last_trigger_time: float = 0.0
        self._is_pinched = False
        self._was_pinched = False
    
    @property
    def state(self) -> GestureState:
        """Get current state."""
        return self._state
    
    @property
    def is_pinched(self) -> bool:
        """Check if currently pinched."""
        return self._is_pinched
    
    @property
    def is_holding(self) -> bool:
        """Check if in hold state."""
        return self._state == GestureState.HOLDING
    
    def update(self, distance: float) -> GestureState:
        """Update pinch state based on finger distance.
        
        Args:
            distance: Normalized distance between fingers
            
        Returns:
            Current gesture state
        """
        current_time = time.time() * 1000  # Convert to ms
        self._was_pinched = self._is_pinched
        self._is_pinched = distance < self.threshold
        
        if self._state == GestureState.IDLE:
            if self._is_pinched:
                # Check debounce
                if current_time - self._last_trigger_time > self.debounce_ms:
                    self._state = GestureState.TRIGGERED
                    self._pinch_start_time = current_time
                    
        elif self._state == GestureState.TRIGGERED:
            if not self._is_pinched:
                # Released quickly = click
                self._state = GestureState.RELEASED
                self._last_trigger_time = current_time
            elif self._pinch_start_time:
                # Check if holding
                if current_time - self._pinch_start_time > self.hold_ms:
                    self._state = GestureState.HOLDING
                    
        elif self._state == GestureState.HOLDING:
            if not self._is_pinched:
                self._state = GestureState.RELEASED
                self._last_trigger_time = current_time
                
        elif self._state == GestureState.RELEASED:
            # Transition back to idle
            self._state = GestureState.IDLE
            self._pinch_start_time = None
        
        return self._state
    
    def reset(self) -> None:
        """Reset detector state."""
        self._state = GestureState.IDLE
        self._pinch_start_time = None
        self._is_pinched = False
        self._was_pinched = False


class GestureEngine:
    """Main gesture detection engine.
    
    Processes hand landmark data to detect various gestures.
    Supports callbacks for gesture events.
    
    Example:
        >>> engine = GestureEngine()
        >>> engine.on_gesture(GestureType.LEFT_CLICK, handle_click)
        >>> gesture = engine.process(hand_data)
    """
    
    def __init__(self, config: Optional[GestureConfig] = None) -> None:
        """Initialize gesture engine.
        
        Args:
            config: Gesture configuration
        """
        self.config = config or GestureConfig()
        
        # Pinch detectors
        self._left_pinch = PinchDetector(
            threshold=self.config.pinch_threshold,
            debounce_ms=self.config.debounce_ms,
            hold_ms=self.config.hold_time_ms
        )
        self._right_pinch = PinchDetector(
            threshold=self.config.pinch_threshold,
            debounce_ms=self.config.debounce_ms,
            hold_ms=self.config.hold_time_ms
        )
        
        # Gesture callbacks
        self._callbacks: Dict[GestureType, List[Callable[[Gesture], None]]] = {
            gesture_type: [] for gesture_type in GestureType
        }
        
        # Tracking state
        self._last_position: Optional[tuple[float, float]] = None
        self._is_dragging = False
        
        logger.info(
            "GestureEngine initialized: pinch_threshold=%.3f, debounce=%dms",
            self.config.pinch_threshold,
            self.config.debounce_ms
        )
    
    def on_gesture(
        self, 
        gesture_type: GestureType, 
        callback: Callable[[Gesture], None]
    ) -> None:
        """Register callback for gesture type.
        
        Args:
            gesture_type: Type of gesture to listen for
            callback: Function to call when gesture detected
        """
        self._callbacks[gesture_type].append(callback)
        logger.debug("Registered callback for %s", gesture_type.name)
    
    def off_gesture(
        self, 
        gesture_type: GestureType, 
        callback: Callable[[Gesture], None]
    ) -> None:
        """Unregister callback for gesture type.
        
        Args:
            gesture_type: Type of gesture
            callback: Callback to remove
        """
        if callback in self._callbacks[gesture_type]:
            self._callbacks[gesture_type].remove(callback)
    
    def process(self, hand: HandData) -> List[Gesture]:
        """Process hand data and detect gestures.
        
        Args:
            hand: Hand landmark data
            
        Returns:
            List of detected gestures
        """
        gestures: List[Gesture] = []
        
        if not hand.is_valid:
            self._reset_on_no_hand()
            return gestures
        
        # Get finger positions
        thumb_tip = hand.thumb_tip
        index_tip = hand.index_tip
        middle_tip = hand.middle_tip
        
        if not all([thumb_tip, index_tip, middle_tip]):
            return gestures
        
        # Current cursor position (from index finger)
        cursor_pos = (index_tip.x, index_tip.y)
        
        # Calculate pinch distances
        left_distance = thumb_tip.distance_to(index_tip)
        right_distance = thumb_tip.distance_to(middle_tip)
        
        # Update pinch detectors
        left_state = self._left_pinch.update(left_distance)
        right_state = self._right_pinch.update(right_distance)
        
        # Handle cursor movement
        cursor_gesture = self._process_cursor_move(cursor_pos)
        if cursor_gesture:
            gestures.append(cursor_gesture)
        
        # Handle left click/drag (thumb + index)
        left_gestures = self._process_left_pinch(left_state, cursor_pos)
        gestures.extend(left_gestures)
        
        # Handle right click (thumb + middle)
        right_gesture = self._process_right_pinch(right_state, cursor_pos)
        if right_gesture:
            gestures.append(right_gesture)
        
        # Trigger callbacks
        for gesture in gestures:
            self._trigger_callbacks(gesture)
        
        # Update last position
        self._last_position = cursor_pos
        
        return gestures
    
    def _process_cursor_move(
        self, 
        position: tuple[float, float]
    ) -> Optional[Gesture]:
        """Process cursor movement.
        
        Args:
            position: Current cursor position
            
        Returns:
            Cursor move gesture or None
        """
        if self._last_position is None:
            return None
        
        # Calculate movement delta
        dx = abs(position[0] - self._last_position[0])
        dy = abs(position[1] - self._last_position[1])
        
        # Only emit if moved significantly
        if dx > self.config.velocity_threshold or dy > self.config.velocity_threshold:
            return Gesture(
                type=GestureType.CURSOR_MOVE,
                position=position,
                metadata={"delta": (dx, dy)}
            )
        
        return None
    
    def _process_left_pinch(
        self, 
        state: GestureState, 
        position: tuple[float, float]
    ) -> List[Gesture]:
        """Process left pinch (click/drag).
        
        Args:
            state: Current pinch state
            position: Current position
            
        Returns:
            List of gestures
        """
        gestures = []
        
        if state == GestureState.TRIGGERED:
            if not self._is_dragging:
                # Start potential drag
                pass
                
        elif state == GestureState.HOLDING:
            if not self._is_dragging:
                # Start drag
                self._is_dragging = True
                gestures.append(Gesture(
                    type=GestureType.DRAG_START,
                    position=position
                ))
            else:
                # Continue drag
                gestures.append(Gesture(
                    type=GestureType.DRAG_MOVE,
                    position=position
                ))
                
        elif state == GestureState.RELEASED:
            if self._is_dragging:
                # End drag
                self._is_dragging = False
                gestures.append(Gesture(
                    type=GestureType.DRAG_END,
                    position=position
                ))
            else:
                # Regular click
                gestures.append(Gesture(
                    type=GestureType.LEFT_CLICK,
                    position=position
                ))
        
        return gestures
    
    def _process_right_pinch(
        self, 
        state: GestureState, 
        position: tuple[float, float]
    ) -> Optional[Gesture]:
        """Process right pinch (right click).
        
        Args:
            state: Current pinch state
            position: Current position
            
        Returns:
            Right click gesture or None
        """
        if state == GestureState.RELEASED:
            return Gesture(
                type=GestureType.RIGHT_CLICK,
                position=position
            )
        return None
    
    def _trigger_callbacks(self, gesture: Gesture) -> None:
        """Trigger callbacks for gesture.
        
        Args:
            gesture: Detected gesture
        """
        for callback in self._callbacks[gesture.type]:
            try:
                callback(gesture)
            except Exception as e:
                logger.error("Callback error for %s: %s", gesture.type.name, e)
    
    def _reset_on_no_hand(self) -> None:
        """Reset state when no hand detected."""
        if self._is_dragging:
            # End any active drag
            self._is_dragging = False
            gesture = Gesture(
                type=GestureType.DRAG_END,
                position=self._last_position or (0, 0)
            )
            self._trigger_callbacks(gesture)
        
        self._left_pinch.reset()
        self._right_pinch.reset()
        self._last_position = None
    
    def reset(self) -> None:
        """Reset engine state."""
        self._left_pinch.reset()
        self._right_pinch.reset()
        self._last_position = None
        self._is_dragging = False
        logger.debug("Gesture engine reset")
