"""
Camera Manager Module

Handles webcam capture, frame processing, and resource management.
Provides a clean interface for accessing camera frames with automatic
reconnection and error handling.
"""

from __future__ import annotations

import time
import threading
from typing import Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraState(Enum):
    """Camera connection states."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()


@dataclass
class CameraConfig:
    """Camera configuration parameters.
    
    Attributes:
        device_index: Camera device index (0 for default)
        resolution: Tuple of (width, height)
        fps: Target frames per second
        auto_reconnect: Whether to attempt reconnection on disconnect
        reconnect_delay: Seconds to wait before reconnect attempt
        warmup_frames: Number of frames to skip during initialization
    """
    device_index: int = 0
    resolution: Tuple[int, int] = (1280, 720)
    fps: int = 30
    auto_reconnect: bool = True
    reconnect_delay: float = 2.0
    warmup_frames: int = 10
    
    @classmethod
    def from_dict(cls, data: dict) -> CameraConfig:
        """Create config from dictionary."""
        return cls(
            device_index=data.get("device_index", 0),
            resolution=tuple(data.get("resolution", [1280, 720])),
            fps=data.get("fps", 30),
            auto_reconnect=data.get("auto_reconnect", True),
            reconnect_delay=data.get("reconnect_delay", 2.0),
            warmup_frames=data.get("warmup_frames", 10),
        )


class CameraManager:
    """Manages webcam capture and frame access.
    
    This class handles all camera-related operations including initialization,
    frame capture, and graceful cleanup. It runs capture in a background
    thread to prevent blocking the main loop.
    
    Attributes:
        config: Camera configuration
        state: Current camera state
        
    Example:
        >>> camera = CameraManager(CameraConfig())
        >>> camera.start()
        >>> while True:
        ...     frame = camera.get_frame()
        ...     if frame is not None:
        ...         process(frame)
        >>> camera.stop()
    """
    
    def __init__(self, config: Optional[CameraConfig] = None) -> None:
        """Initialize camera manager.
        
        Args:
            config: Camera configuration, uses defaults if not provided
        """
        self.config = config or CameraConfig()
        self._state = CameraState.DISCONNECTED
        self._capture: Optional[cv2.VideoCapture] = None
        self._frame: Optional[np.ndarray] = None
        self._frame_lock = threading.Lock()
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None
        self._frame_count = 0
        self._fps_actual = 0.0
        self._last_fps_time = time.time()
        self._fps_frame_count = 0
        self._on_state_change: Optional[Callable[[CameraState], None]] = None
        
        logger.info(
            "CameraManager initialized with device=%d, resolution=%s, fps=%d",
            self.config.device_index,
            self.config.resolution,
            self.config.fps
        )
    
    @property
    def state(self) -> CameraState:
        """Get current camera state."""
        return self._state
    
    @state.setter
    def state(self, new_state: CameraState) -> None:
        """Set camera state and notify listeners."""
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            logger.info("Camera state: %s -> %s", old_state.name, new_state.name)
            if self._on_state_change:
                try:
                    self._on_state_change(new_state)
                except Exception as e:
                    logger.error("Error in state change callback: %s", e)
    
    @property
    def fps(self) -> float:
        """Get actual frames per second."""
        return self._fps_actual
    
    @property
    def frame_count(self) -> int:
        """Get total frames captured."""
        return self._frame_count
    
    @property
    def is_connected(self) -> bool:
        """Check if camera is connected and capturing."""
        return self._state == CameraState.CONNECTED and self._running
    
    def on_state_change(self, callback: Callable[[CameraState], None]) -> None:
        """Register callback for state changes.
        
        Args:
            callback: Function to call when state changes
        """
        self._on_state_change = callback
    
    def start(self) -> bool:
        """Start camera capture.
        
        Returns:
            True if camera started successfully, False otherwise
        """
        if self._running:
            logger.warning("Camera already running")
            return True
        
        logger.info("Starting camera...")
        self.state = CameraState.CONNECTING
        
        if not self._initialize_capture():
            self.state = CameraState.ERROR
            return False
        
        self._running = True
        self._capture_thread = threading.Thread(
            target=self._capture_loop,
            name="CameraCapture",
            daemon=True
        )
        self._capture_thread.start()
        
        # Wait for warmup frames
        warmup_start = time.time()
        while self._frame_count < self.config.warmup_frames:
            if time.time() - warmup_start > 5.0:
                logger.error("Camera warmup timeout")
                self.stop()
                return False
            time.sleep(0.1)
        
        self.state = CameraState.CONNECTED
        logger.info("Camera started successfully")
        return True
    
    def stop(self) -> None:
        """Stop camera capture and release resources."""
        logger.info("Stopping camera...")
        self._running = False
        
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=2.0)
        
        self._release_capture()
        self.state = CameraState.DISCONNECTED
        logger.info("Camera stopped")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest captured frame.
        
        Returns:
            BGR image as numpy array, or None if no frame available
        """
        with self._frame_lock:
            if self._frame is not None:
                return self._frame.copy()
        return None
    
    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """Get the latest frame in RGB format.
        
        Returns:
            RGB image as numpy array, or None if no frame available
        """
        frame = self.get_frame()
        if frame is not None:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None
    
    def _initialize_capture(self) -> bool:
        """Initialize video capture device.
        
        Returns:
            True if initialization successful
        """
        try:
            # Use DirectShow backend on Windows for better compatibility
            self._capture = cv2.VideoCapture(
                self.config.device_index,
                cv2.CAP_DSHOW
            )
            
            if not self._capture.isOpened():
                logger.error("Failed to open camera device %d", self.config.device_index)
                return False
            
            # Set camera properties
            width, height = self.config.resolution
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self._capture.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Reduce buffer size to minimize latency
            self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Verify settings
            actual_width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self._capture.get(cv2.CAP_PROP_FPS)
            
            logger.info(
                "Camera initialized: %dx%d @ %.1f FPS",
                actual_width, actual_height, actual_fps
            )
            
            return True
            
        except Exception as e:
            logger.error("Camera initialization error: %s", e)
            return False
    
    def _release_capture(self) -> None:
        """Release video capture resources."""
        if self._capture is not None:
            try:
                self._capture.release()
            except Exception as e:
                logger.error("Error releasing camera: %s", e)
            finally:
                self._capture = None
    
    def _capture_loop(self) -> None:
        """Main capture loop running in background thread."""
        frame_interval = 1.0 / self.config.fps
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self._running:
            loop_start = time.time()
            
            try:
                if self._capture is None or not self._capture.isOpened():
                    if self.config.auto_reconnect and reconnect_attempts < max_reconnect_attempts:
                        logger.warning("Camera disconnected, attempting reconnect...")
                        self.state = CameraState.CONNECTING
                        time.sleep(self.config.reconnect_delay)
                        
                        if self._initialize_capture():
                            reconnect_attempts = 0
                            self.state = CameraState.CONNECTED
                            logger.info("Camera reconnected successfully")
                        else:
                            reconnect_attempts += 1
                            logger.warning(
                                "Reconnect attempt %d/%d failed",
                                reconnect_attempts, max_reconnect_attempts
                            )
                    else:
                        self.state = CameraState.ERROR
                        logger.error("Camera reconnection failed, giving up")
                        break
                    continue
                
                ret, frame = self._capture.read()
                
                if not ret or frame is None:
                    logger.warning("Failed to read frame")
                    continue
                
                # Update frame (thread-safe)
                with self._frame_lock:
                    self._frame = frame
                
                self._frame_count += 1
                self._update_fps()
                
                # Reset reconnect counter on successful read
                reconnect_attempts = 0
                
            except Exception as e:
                logger.error("Capture loop error: %s", e)
                self.state = CameraState.ERROR
            
            # Frame rate limiting
            elapsed = time.time() - loop_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _update_fps(self) -> None:
        """Update FPS calculation."""
        self._fps_frame_count += 1
        current_time = time.time()
        elapsed = current_time - self._last_fps_time
        
        if elapsed >= 1.0:
            self._fps_actual = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._last_fps_time = current_time
    
    def __enter__(self) -> CameraManager:
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
    
    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        self.stop()
