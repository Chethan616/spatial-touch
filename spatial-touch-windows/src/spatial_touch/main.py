"""
Spatial Touch - Main Controller

Entry point and main orchestrator for the Spatial Touch application.
Coordinates camera, tracking, gesture detection, and action dispatch.
"""

from __future__ import annotations

import sys
import signal
import time
import argparse
import json
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
import logging

from spatial_touch.core.camera import CameraManager, CameraConfig, CameraState
from spatial_touch.core.hand_tracker import HandTracker, TrackerConfig, HandData
from spatial_touch.core.gesture_engine import GestureEngine, GestureConfig, Gesture, GestureType
from spatial_touch.core.zone_mapper import ZoneMapper, ZoneConfig, get_screen_size
from spatial_touch.core.action_dispatcher import ActionDispatcher, ActionConfig
from spatial_touch.utils.logger import setup_logging, get_logger, PerformanceLogger

logger = get_logger(__name__)


@dataclass
class AppConfig:
    """Application configuration.
    
    Attributes:
        camera: Camera settings
        tracking: Hand tracking settings
        gestures: Gesture detection settings
        cursor: Zone mapping settings
        actions: Action dispatcher settings
        system: System settings
    """
    camera: CameraConfig
    tracking: TrackerConfig
    gestures: GestureConfig
    cursor: ZoneConfig
    actions: ActionConfig
    
    # System settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    debug_mode: bool = False
    idle_fps: int = 5
    active_fps: int = 30
    idle_timeout_frames: int = 30
    
    @classmethod
    def from_file(cls, path: str) -> AppConfig:
        """Load configuration from JSON file.
        
        Args:
            path: Path to settings.json
            
        Returns:
            AppConfig instance
        """
        config_path = Path(path)
        
        if not config_path.exists():
            logger.warning("Config file not found: %s, using defaults", path)
            return cls.default()
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return cls(
            camera=CameraConfig.from_dict(data.get("camera", {})),
            tracking=TrackerConfig.from_dict(data.get("tracking", {})),
            gestures=GestureConfig.from_dict(data.get("gestures", {})),
            cursor=ZoneConfig.from_dict(data.get("cursor", {})),
            actions=ActionConfig.from_dict(data.get("actions", {})),
            log_level=data.get("system", {}).get("log_level", "INFO"),
            log_file=data.get("system", {}).get("log_file"),
            debug_mode=data.get("system", {}).get("debug_mode", False),
            idle_fps=data.get("system", {}).get("idle_fps", 5),
            active_fps=data.get("system", {}).get("active_fps", 30),
            idle_timeout_frames=data.get("system", {}).get("idle_timeout_frames", 30),
        )
    
    @classmethod
    def default(cls) -> AppConfig:
        """Create default configuration.
        
        Returns:
            Default AppConfig
        """
        # Get actual screen size
        screen_width, screen_height = get_screen_size()
        
        zone_config = ZoneConfig(
            screen_width=screen_width,
            screen_height=screen_height
        )
        
        return cls(
            camera=CameraConfig(),
            tracking=TrackerConfig(),
            gestures=GestureConfig(),
            cursor=zone_config,
            actions=ActionConfig(),
        )


class SpatialTouchController:
    """Main controller for Spatial Touch.
    
    Orchestrates all components and manages the main processing loop.
    
    Example:
        >>> controller = SpatialTouchController()
        >>> controller.start()  # Blocks until stopped
        
        # Or with context manager
        >>> with SpatialTouchController() as ctrl:
        ...     time.sleep(60)  # Run for 60 seconds
    """
    
    def __init__(self, config: Optional[AppConfig] = None) -> None:
        """Initialize controller.
        
        Args:
            config: Application configuration
        """
        self.config = config or AppConfig.default()
        
        # Components
        self._camera: Optional[CameraManager] = None
        self._tracker: Optional[HandTracker] = None
        self._gesture_engine: Optional[GestureEngine] = None
        self._zone_mapper: Optional[ZoneMapper] = None
        self._dispatcher: Optional[ActionDispatcher] = None
        
        # State
        self._running = False
        self._paused = False
        self._frame_count = 0
        self._idle_frame_count = 0
        
        # Performance tracking
        self._perf_capture = PerformanceLogger("capture")
        self._perf_tracking = PerformanceLogger("tracking")
        self._perf_gesture = PerformanceLogger("gesture")
        self._perf_total = PerformanceLogger("total")
        
        # Callbacks
        self._on_gesture_callbacks: list[Callable[[Gesture], None]] = []
        self._on_error_callbacks: list[Callable[[Exception], None]] = []
        
        logger.info("SpatialTouchController initialized")
    
    @property
    def is_running(self) -> bool:
        """Check if controller is running."""
        return self._running
    
    @property
    def is_paused(self) -> bool:
        """Check if controller is paused."""
        return self._paused
    
    @property
    def frame_count(self) -> int:
        """Get total frames processed."""
        return self._frame_count
    
    def on_gesture(self, callback: Callable[[Gesture], None]) -> None:
        """Register gesture callback.
        
        Args:
            callback: Function to call on gesture detection
        """
        self._on_gesture_callbacks.append(callback)
    
    def on_error(self, callback: Callable[[Exception], None]) -> None:
        """Register error callback.
        
        Args:
            callback: Function to call on error
        """
        self._on_error_callbacks.append(callback)
    
    def start(self, blocking: bool = True) -> None:
        """Start the controller.
        
        Args:
            blocking: If True, blocks until stopped
        """
        if self._running:
            logger.warning("Controller already running")
            return
        
        logger.info("Starting Spatial Touch...")
        
        try:
            self._initialize_components()
            self._running = True
            
            # Setup signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            logger.info("Spatial Touch started successfully")
            
            if blocking:
                self._main_loop()
            
        except Exception as e:
            logger.error("Failed to start: %s", e)
            self._notify_error(e)
            self.stop()
            raise
    
    def stop(self) -> None:
        """Stop the controller."""
        if not self._running:
            return
        
        logger.info("Stopping Spatial Touch...")
        self._running = False
        
        self._cleanup_components()
        
        # Log performance stats
        self._log_performance_stats()
        
        logger.info("Spatial Touch stopped")
    
    def pause(self) -> None:
        """Pause gesture detection."""
        self._paused = True
        logger.info("Spatial Touch paused")
    
    def resume(self) -> None:
        """Resume gesture detection."""
        self._paused = False
        logger.info("Spatial Touch resumed")
    
    def toggle_pause(self) -> bool:
        """Toggle pause state.
        
        Returns:
            New pause state
        """
        if self._paused:
            self.resume()
        else:
            self.pause()
        return self._paused
    
    def _initialize_components(self) -> None:
        """Initialize all components."""
        logger.debug("Initializing components...")
        
        # Camera
        self._camera = CameraManager(self.config.camera)
        self._camera.on_state_change(self._on_camera_state_change)
        if not self._camera.start():
            raise RuntimeError("Failed to start camera")
        
        # Hand tracker
        self._tracker = HandTracker(self.config.tracking)
        self._tracker.start()
        
        # Gesture engine
        self._gesture_engine = GestureEngine(self.config.gestures)
        
        # Zone mapper
        self._zone_mapper = ZoneMapper(self.config.cursor)
        
        # Action dispatcher
        self._dispatcher = ActionDispatcher(self.config.actions)
        self._dispatcher.start()
        
        logger.debug("All components initialized")
    
    def _cleanup_components(self) -> None:
        """Cleanup all components."""
        logger.debug("Cleaning up components...")
        
        if self._dispatcher:
            self._dispatcher.stop()
            self._dispatcher = None
        
        if self._tracker:
            self._tracker.stop()
            self._tracker = None
        
        if self._camera:
            self._camera.stop()
            self._camera = None
        
        self._gesture_engine = None
        self._zone_mapper = None
        
        logger.debug("Components cleaned up")
    
    def _main_loop(self) -> None:
        """Main processing loop."""
        logger.debug("Entering main loop...")
        
        target_interval = 1.0 / self.config.active_fps
        idle_interval = 1.0 / self.config.idle_fps
        
        while self._running:
            loop_start = time.perf_counter()
            
            try:
                self._perf_total.start()
                
                if not self._paused:
                    self._process_frame()
                
                self._perf_total.end(log=False)
                
                # Adaptive frame rate
                is_idle = self._idle_frame_count > self.config.idle_timeout_frames
                interval = idle_interval if is_idle else target_interval
                
                # Frame rate limiting
                elapsed = time.perf_counter() - loop_start
                sleep_time = interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error("Error in main loop: %s", e)
                self._notify_error(e)
        
        logger.debug("Exited main loop")
    
    def _process_frame(self) -> None:
        """Process a single frame."""
        if not all([self._camera, self._tracker, self._gesture_engine, 
                    self._zone_mapper, self._dispatcher]):
            return
        
        # Capture frame
        self._perf_capture.start()
        frame = self._camera.get_frame_rgb()
        self._perf_capture.end(log=False)
        
        if frame is None:
            return
        
        self._frame_count += 1
        
        # Track hand
        self._perf_tracking.start()
        hand = self._tracker.process(frame)
        self._perf_tracking.end(log=False)
        
        # Update idle counter
        if not hand.is_valid:
            self._idle_frame_count += 1
            return
        else:
            self._idle_frame_count = 0
        
        # Detect gestures
        self._perf_gesture.start()
        gestures = self._gesture_engine.process(hand)
        self._perf_gesture.end(log=False)
        
        # Process gestures
        for gesture in gestures:
            self._handle_gesture(gesture, hand)
    
    def _handle_gesture(self, gesture: Gesture, hand: HandData) -> None:
        """Handle detected gesture.
        
        Args:
            gesture: Detected gesture
            hand: Hand data
        """
        # Map position to screen
        if gesture.position:
            screen_pos = self._zone_mapper.map_position(gesture.position)
            gesture.metadata["screen_pos"] = (screen_pos.x, screen_pos.y)
            
            # Move cursor for cursor_move and drag gestures
            if gesture.type in (GestureType.CURSOR_MOVE, GestureType.DRAG_MOVE):
                self._dispatcher.move_cursor(screen_pos.x, screen_pos.y)
        
        # Dispatch to action handler
        self._dispatcher.handle_gesture(gesture)
        
        # Notify callbacks
        for callback in self._on_gesture_callbacks:
            try:
                callback(gesture)
            except Exception as e:
                logger.error("Gesture callback error: %s", e)
    
    def _on_camera_state_change(self, state: CameraState) -> None:
        """Handle camera state changes.
        
        Args:
            state: New camera state
        """
        if state == CameraState.ERROR:
            logger.error("Camera error, stopping...")
            self.stop()
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle system signals."""
        logger.info("Received signal %s, stopping...", signum)
        self.stop()
    
    def _notify_error(self, error: Exception) -> None:
        """Notify error callbacks.
        
        Args:
            error: Exception that occurred
        """
        for callback in self._on_error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error("Error callback failed: %s", e)
    
    def _log_performance_stats(self) -> None:
        """Log performance statistics."""
        logger.info("=== Performance Statistics ===")
        logger.info("Total frames: %d", self._frame_count)
        logger.info("Capture: avg=%.2fms", self._perf_capture.average)
        logger.info("Tracking: avg=%.2fms", self._perf_tracking.average)
        logger.info("Gesture: avg=%.2fms", self._perf_gesture.average)
        logger.info("Total: avg=%.2fms", self._perf_total.average)
    
    def __enter__(self) -> SpatialTouchController:
        """Context manager entry."""
        self.start(blocking=False)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Spatial Touch - Touchless Computer Control",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/settings.json",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--camera", "-cam",
        type=int,
        default=0,
        help="Camera device index"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Spatial Touch 0.1.0"
    )
    
    parser.add_argument(
        "--api", "-a",
        action="store_true",
        help="Enable REST API server"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=8765,
        help="API server port (default: 8765)"
    )
    
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Run only the API server (for Flutter app control)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = AppConfig.from_file(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        config = AppConfig.default()
    
    # Apply command line overrides
    if args.debug:
        config.debug_mode = True
        config.log_level = "DEBUG"
    
    if args.camera:
        config.camera.device_index = args.camera
    
    if args.log_file:
        config.log_file = args.log_file
    
    # Setup logging
    setup_logging(
        level=config.log_level,
        log_file=config.log_file,
        console=True
    )
    
    logger.info("Spatial Touch v0.1.0")
    logger.info("Press Ctrl+C to exit")
    
    # Initialize API server if requested
    api_server = None
    if args.api or args.api_only:
        from spatial_touch.api import APIServer, APIServerConfig
        from pathlib import Path
        
        api_config = APIServerConfig(port=args.api_port)
        config_path = Path(args.config).resolve()
        gestures_path = config_path.parent / "gestures.json"
        
        api_server = APIServer(
            config=api_config,
            config_path=config_path,
            gestures_path=gestures_path
        )
    
    # Run controller
    try:
        controller = SpatialTouchController(config)
        
        # Connect API server to controller
        if api_server:
            api_server.set_controller(controller)
            api_server.start()
            logger.info("API server running at http://localhost:%d", args.api_port)
            logger.info("API docs available at http://localhost:%d/docs", args.api_port)
        
        if args.api_only:
            # API-only mode: just keep the server running
            logger.info("Running in API-only mode. Use Flutter app to control.")
            import time
            while True:
                time.sleep(1)
        else:
            controller.start(blocking=True)
        
        return 0
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        if api_server:
            api_server.stop()
        return 0
    except Exception as e:
        logger.error("Fatal error: %s", e)
        if api_server:
            api_server.stop()
        return 1


if __name__ == "__main__":
    sys.exit(main())
