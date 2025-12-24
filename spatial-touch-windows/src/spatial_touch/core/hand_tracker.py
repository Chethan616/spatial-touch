"""
Hand Tracker Module

Integrates MediaPipe Hands for real-time hand landmark detection.
Provides smoothed landmark data with confidence filtering.
"""

from __future__ import annotations

import logging
from typing import Optional, List, NamedTuple, Tuple
from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np
import mediapipe as mp

from spatial_touch.utils.smoothing import ExponentialMovingAverage

logger = logging.getLogger(__name__)


class HandLandmark(IntEnum):
    """MediaPipe hand landmark indices.
    
    Reference: https://google.github.io/mediapipe/solutions/hands.html
    """
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


class Point3D(NamedTuple):
    """3D point with x, y, z coordinates (normalized 0-1)."""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: Point3D) -> float:
        """Calculate Euclidean distance to another point."""
        return np.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple."""
        return (self.x, self.y, self.z)
    
    def to_2d(self) -> Tuple[float, float]:
        """Get 2D coordinates (x, y)."""
        return (self.x, self.y)


@dataclass
class HandData:
    """Processed hand landmark data.
    
    Attributes:
        landmarks: List of 21 hand landmarks as Point3D
        handedness: 'Left' or 'Right'
        confidence: Detection confidence score (0-1)
        is_valid: Whether the hand data is valid
    """
    landmarks: List[Point3D] = field(default_factory=list)
    handedness: str = "Unknown"
    confidence: float = 0.0
    is_valid: bool = False
    
    @property
    def wrist(self) -> Optional[Point3D]:
        """Get wrist landmark."""
        return self._get_landmark(HandLandmark.WRIST)
    
    @property
    def thumb_tip(self) -> Optional[Point3D]:
        """Get thumb tip landmark."""
        return self._get_landmark(HandLandmark.THUMB_TIP)
    
    @property
    def index_tip(self) -> Optional[Point3D]:
        """Get index finger tip landmark."""
        return self._get_landmark(HandLandmark.INDEX_TIP)
    
    @property
    def middle_tip(self) -> Optional[Point3D]:
        """Get middle finger tip landmark."""
        return self._get_landmark(HandLandmark.MIDDLE_TIP)
    
    @property
    def ring_tip(self) -> Optional[Point3D]:
        """Get ring finger tip landmark."""
        return self._get_landmark(HandLandmark.RING_TIP)
    
    @property
    def pinky_tip(self) -> Optional[Point3D]:
        """Get pinky finger tip landmark."""
        return self._get_landmark(HandLandmark.PINKY_TIP)
    
    def _get_landmark(self, index: HandLandmark) -> Optional[Point3D]:
        """Get landmark by index safely."""
        if self.is_valid and 0 <= index < len(self.landmarks):
            return self.landmarks[index]
        return None
    
    def get_landmark(self, index: int) -> Optional[Point3D]:
        """Get landmark by index.
        
        Args:
            index: Landmark index (0-20)
            
        Returns:
            Point3D or None if invalid
        """
        return self._get_landmark(HandLandmark(index))


@dataclass
class TrackerConfig:
    """Hand tracker configuration.
    
    Attributes:
        max_hands: Maximum number of hands to detect
        min_detection_confidence: Minimum detection confidence
        min_tracking_confidence: Minimum tracking confidence
        model_complexity: Model complexity (0, 1)
        smoothing_factor: Landmark smoothing factor (0-1)
        static_image_mode: Use static image mode (slower but more accurate)
    """
    max_hands: int = 1
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.5
    model_complexity: int = 1
    smoothing_factor: float = 0.4
    static_image_mode: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> TrackerConfig:
        """Create config from dictionary."""
        return cls(
            max_hands=data.get("max_hands", 1),
            min_detection_confidence=data.get("min_detection_confidence", 0.7),
            min_tracking_confidence=data.get("min_tracking_confidence", 0.5),
            model_complexity=data.get("model_complexity", 1),
            smoothing_factor=data.get("smoothing_factor", 0.4),
            static_image_mode=data.get("static_image_mode", False),
        )


class HandTracker:
    """Real-time hand tracking using MediaPipe.
    
    Processes camera frames to detect and track hand landmarks.
    Provides smoothed landmark data for stable gesture detection.
    
    Example:
        >>> tracker = HandTracker()
        >>> tracker.start()
        >>> hand = tracker.process(frame)
        >>> if hand.is_valid:
        ...     print(f"Index tip: {hand.index_tip}")
        >>> tracker.stop()
    """
    
    NUM_LANDMARKS = 21
    
    def __init__(self, config: Optional[TrackerConfig] = None) -> None:
        """Initialize hand tracker.
        
        Args:
            config: Tracker configuration
        """
        self.config = config or TrackerConfig()
        self._hands: Optional[mp.solutions.hands.Hands] = None
        self._smoothers: List[ExponentialMovingAverage] = []
        self._is_running = False
        self._last_hand: Optional[HandData] = None
        self._frames_without_hand = 0
        
        logger.info(
            "HandTracker initialized: max_hands=%d, detection_conf=%.2f, "
            "tracking_conf=%.2f, smoothing=%.2f",
            self.config.max_hands,
            self.config.min_detection_confidence,
            self.config.min_tracking_confidence,
            self.config.smoothing_factor
        )
    
    @property
    def is_running(self) -> bool:
        """Check if tracker is running."""
        return self._is_running
    
    @property
    def last_hand(self) -> Optional[HandData]:
        """Get last detected hand data."""
        return self._last_hand
    
    @property
    def frames_without_hand(self) -> int:
        """Get count of consecutive frames without hand detection."""
        return self._frames_without_hand
    
    def start(self) -> None:
        """Initialize MediaPipe Hands and start tracking."""
        if self._is_running:
            logger.warning("Tracker already running")
            return
        
        logger.info("Starting hand tracker...")
        
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=self.config.static_image_mode,
            max_num_hands=self.config.max_hands,
            min_detection_confidence=self.config.min_detection_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence,
            model_complexity=self.config.model_complexity,
        )
        
        # Initialize smoothers for each landmark coordinate (21 landmarks × 3 coords)
        self._smoothers = [
            ExponentialMovingAverage(alpha=self.config.smoothing_factor)
            for _ in range(self.NUM_LANDMARKS * 3)
        ]
        
        self._is_running = True
        self._frames_without_hand = 0
        
        logger.info("Hand tracker started")
    
    def stop(self) -> None:
        """Stop tracking and release resources."""
        if not self._is_running:
            return
        
        logger.info("Stopping hand tracker...")
        
        if self._hands is not None:
            self._hands.close()
            self._hands = None
        
        self._smoothers.clear()
        self._is_running = False
        self._last_hand = None
        
        logger.info("Hand tracker stopped")
    
    def process(self, frame: np.ndarray) -> HandData:
        """Process a frame and detect hand landmarks.
        
        Args:
            frame: RGB image as numpy array
            
        Returns:
            HandData with detected landmarks
        """
        if not self._is_running or self._hands is None:
            logger.warning("Tracker not running, call start() first")
            return HandData()
        
        try:
            # Process frame with MediaPipe
            results = self._hands.process(frame)
            
            if not results.multi_hand_landmarks:
                self._frames_without_hand += 1
                self._last_hand = HandData()
                return self._last_hand
            
            # Reset counter on detection
            self._frames_without_hand = 0
            
            # Get first hand (primary hand)
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Get handedness
            handedness = "Unknown"
            confidence = 0.0
            if results.multi_handedness:
                hand_info = results.multi_handedness[0].classification[0]
                # MediaPipe returns mirrored handedness, so flip it
                handedness = "Right" if hand_info.label == "Left" else "Left"
                confidence = hand_info.score
            
            # Extract and smooth landmarks
            landmarks = self._extract_landmarks(hand_landmarks)
            smoothed_landmarks = self._smooth_landmarks(landmarks)
            
            self._last_hand = HandData(
                landmarks=smoothed_landmarks,
                handedness=handedness,
                confidence=confidence,
                is_valid=True
            )
            
            return self._last_hand
            
        except Exception as e:
            logger.error("Hand processing error: %s", e)
            return HandData()
    
    def _extract_landmarks(
        self, 
        hand_landmarks: mp.solutions.hands.HandLandmark
    ) -> List[Point3D]:
        """Extract landmarks as Point3D list.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            List of 21 Point3D landmarks
        """
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append(Point3D(x=lm.x, y=lm.y, z=lm.z))
        return landmarks
    
    def _smooth_landmarks(self, landmarks: List[Point3D]) -> List[Point3D]:
        """Apply smoothing to landmarks.
        
        Args:
            landmarks: Raw landmark list
            
        Returns:
            Smoothed landmark list
        """
        smoothed = []
        
        for i, point in enumerate(landmarks):
            base_idx = i * 3
            
            smooth_x = self._smoothers[base_idx].update(point.x)
            smooth_y = self._smoothers[base_idx + 1].update(point.y)
            smooth_z = self._smoothers[base_idx + 2].update(point.z)
            
            smoothed.append(Point3D(x=smooth_x, y=smooth_y, z=smooth_z))
        
        return smoothed
    
    def reset_smoothing(self) -> None:
        """Reset all smoothing filters."""
        for smoother in self._smoothers:
            smoother.reset()
        logger.debug("Smoothing filters reset")
    
    def __enter__(self) -> HandTracker:
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
    
    def __del__(self) -> None:
        """Destructor."""
        self.stop()
