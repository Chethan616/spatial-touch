"""
Zone Mapper Module

Maps normalized camera coordinates to screen coordinates.
Handles dead zones, sensitivity, and screen boundary enforcement.
"""

from __future__ import annotations

import logging
from typing import Tuple, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)


class ScreenZone(Enum):
    """Screen zones for zone-based actions."""
    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    MIDDLE_LEFT = auto()
    MIDDLE_CENTER = auto()
    MIDDLE_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_CENTER = auto()
    BOTTOM_RIGHT = auto()


class ScreenPoint(NamedTuple):
    """Screen coordinates in pixels."""
    x: int
    y: int


@dataclass
class ZoneConfig:
    """Zone mapper configuration.
    
    Attributes:
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        sensitivity: Movement sensitivity multiplier
        dead_zone: Dead zone size (normalized 0-1)
        invert_x: Invert horizontal axis
        invert_y: Invert vertical axis (usually not needed)
        margin: Screen edge margin in pixels
        smoothing: Additional position smoothing
    """
    screen_width: int = 1920
    screen_height: int = 1080
    sensitivity: float = 1.0
    dead_zone: float = 0.02
    invert_x: bool = True  # Mirror movement for natural feel
    invert_y: bool = False
    margin: int = 10
    smoothing: float = 0.0
    
    # Zone grid configuration
    zone_columns: int = 3
    zone_rows: int = 3
    
    @classmethod
    def from_dict(cls, data: dict) -> ZoneConfig:
        """Create config from dictionary."""
        return cls(
            screen_width=data.get("screen_width", 1920),
            screen_height=data.get("screen_height", 1080),
            sensitivity=data.get("sensitivity", 1.0),
            dead_zone=data.get("dead_zone", 0.02),
            invert_x=data.get("invert_x", True),
            invert_y=data.get("invert_y", False),
            margin=data.get("margin", 10),
            smoothing=data.get("smoothing", 0.0),
        )


class ZoneMapper:
    """Maps hand coordinates to screen coordinates.
    
    Transforms normalized camera coordinates (0-1) to screen
    pixel coordinates with sensitivity, dead zone, and boundary
    handling.
    
    Example:
        >>> mapper = ZoneMapper(screen_size=(1920, 1080))
        >>> screen_pos = mapper.map_position((0.5, 0.5))
        >>> print(screen_pos)  # ScreenPoint(x=960, y=540)
    """
    
    def __init__(self, config: Optional[ZoneConfig] = None) -> None:
        """Initialize zone mapper.
        
        Args:
            config: Zone configuration
        """
        self.config = config or ZoneConfig()
        self._last_position: Optional[ScreenPoint] = None
        self._center = (0.5, 0.5)
        
        logger.info(
            "ZoneMapper initialized: screen=%dx%d, sensitivity=%.2f, dead_zone=%.3f",
            self.config.screen_width,
            self.config.screen_height,
            self.config.sensitivity,
            self.config.dead_zone
        )
    
    @property
    def screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        return (self.config.screen_width, self.config.screen_height)
    
    @property
    def last_position(self) -> Optional[ScreenPoint]:
        """Get last mapped position."""
        return self._last_position
    
    def update_screen_size(self, width: int, height: int) -> None:
        """Update screen dimensions.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self.config.screen_width = width
        self.config.screen_height = height
        logger.info("Screen size updated: %dx%d", width, height)
    
    def map_position(
        self, 
        normalized_pos: Tuple[float, float]
    ) -> ScreenPoint:
        """Map normalized coordinates to screen pixels.
        
        Args:
            normalized_pos: Position as (x, y) in range 0-1
            
        Returns:
            Screen position in pixels
        """
        x, y = normalized_pos
        
        # Apply inversion (mirroring)
        if self.config.invert_x:
            x = 1.0 - x
        if self.config.invert_y:
            y = 1.0 - y
        
        # Apply sensitivity
        if self.config.sensitivity != 1.0:
            # Scale around center
            x = 0.5 + (x - 0.5) * self.config.sensitivity
            y = 0.5 + (y - 0.5) * self.config.sensitivity
        
        # Clamp to valid range
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        
        # Map to screen coordinates
        screen_x = int(x * self.config.screen_width)
        screen_y = int(y * self.config.screen_height)
        
        # Apply margin constraints
        margin = self.config.margin
        screen_x = max(margin, min(self.config.screen_width - margin, screen_x))
        screen_y = max(margin, min(self.config.screen_height - margin, screen_y))
        
        # Optional smoothing
        if self.config.smoothing > 0 and self._last_position:
            alpha = 1.0 - self.config.smoothing
            screen_x = int(alpha * screen_x + self.config.smoothing * self._last_position.x)
            screen_y = int(alpha * screen_y + self.config.smoothing * self._last_position.y)
        
        position = ScreenPoint(x=screen_x, y=screen_y)
        self._last_position = position
        
        return position
    
    def is_in_dead_zone(
        self, 
        normalized_pos: Tuple[float, float],
        reference_pos: Optional[Tuple[float, float]] = None
    ) -> bool:
        """Check if position is within dead zone.
        
        Args:
            normalized_pos: Current position (0-1)
            reference_pos: Reference position, uses last position if None
            
        Returns:
            True if within dead zone
        """
        if reference_pos is None:
            if self._last_position is None:
                return False
            # Convert last screen position back to normalized
            reference_pos = (
                self._last_position.x / self.config.screen_width,
                self._last_position.y / self.config.screen_height
            )
        
        dx = abs(normalized_pos[0] - reference_pos[0])
        dy = abs(normalized_pos[1] - reference_pos[1])
        
        return dx < self.config.dead_zone and dy < self.config.dead_zone
    
    def get_zone(self, normalized_pos: Tuple[float, float]) -> ScreenZone:
        """Get the screen zone for a position.
        
        Args:
            normalized_pos: Position as (x, y) in range 0-1
            
        Returns:
            ScreenZone enum value
        """
        x, y = normalized_pos
        
        # Apply inversion for consistent zone detection
        if self.config.invert_x:
            x = 1.0 - x
        
        # Determine column (0, 1, 2)
        col = min(int(x * self.config.zone_columns), self.config.zone_columns - 1)
        
        # Determine row (0, 1, 2)
        row = min(int(y * self.config.zone_rows), self.config.zone_rows - 1)
        
        # Map to zone enum
        zone_index = row * self.config.zone_columns + col
        
        zone_map = [
            ScreenZone.TOP_LEFT, ScreenZone.TOP_CENTER, ScreenZone.TOP_RIGHT,
            ScreenZone.MIDDLE_LEFT, ScreenZone.MIDDLE_CENTER, ScreenZone.MIDDLE_RIGHT,
            ScreenZone.BOTTOM_LEFT, ScreenZone.BOTTOM_CENTER, ScreenZone.BOTTOM_RIGHT,
        ]
        
        return zone_map[zone_index] if zone_index < len(zone_map) else ScreenZone.MIDDLE_CENTER
    
    def get_edge_proximity(
        self, 
        normalized_pos: Tuple[float, float],
        threshold: float = 0.1
    ) -> dict[str, bool]:
        """Check proximity to screen edges.
        
        Args:
            normalized_pos: Position as (x, y) in range 0-1
            threshold: Distance threshold for edge detection
            
        Returns:
            Dict with edge proximity flags
        """
        x, y = normalized_pos
        
        # Apply inversion
        if self.config.invert_x:
            x = 1.0 - x
        
        return {
            "left": x < threshold,
            "right": x > (1.0 - threshold),
            "top": y < threshold,
            "bottom": y > (1.0 - threshold),
        }
    
    def reset(self) -> None:
        """Reset mapper state."""
        self._last_position = None
        logger.debug("Zone mapper reset")


def get_screen_size() -> Tuple[int, int]:
    """Get current screen resolution.
    
    Returns:
        Tuple of (width, height) in pixels
    """
    try:
        import ctypes
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return (width, height)
    except Exception as e:
        logger.warning("Could not get screen size: %s, using default", e)
        return (1920, 1080)


def get_multi_monitor_info() -> list[dict]:
    """Get information about all monitors.
    
    Returns:
        List of monitor info dictionaries
    """
    monitors = []
    try:
        import ctypes
        from ctypes import wintypes
        
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            monitors.append({
                "handle": hMonitor,
                "left": lprcMonitor.contents.left,
                "top": lprcMonitor.contents.top,
                "right": lprcMonitor.contents.right,
                "bottom": lprcMonitor.contents.bottom,
            })
            return True
        
        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(wintypes.RECT),
            ctypes.c_double,
        )
        
        ctypes.windll.user32.EnumDisplayMonitors(
            None, None, MonitorEnumProc(callback), 0
        )
    except Exception as e:
        logger.warning("Could not enumerate monitors: %s", e)
    
    return monitors
