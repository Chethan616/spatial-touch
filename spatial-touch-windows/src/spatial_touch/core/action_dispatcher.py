"""
Action Dispatcher Module

Executes OS-level actions in response to gestures.
Handles mouse movement, clicks, keyboard input, and system actions.
"""

from __future__ import annotations

import logging
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod

import pyautogui

from spatial_touch.core.gesture_engine import Gesture, GestureType

logger = logging.getLogger(__name__)

# Configure pyautogui for safety and performance
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0  # No pause between actions


class ActionType(Enum):
    """Types of OS actions."""
    MOUSE_MOVE = auto()
    MOUSE_LEFT_CLICK = auto()
    MOUSE_RIGHT_CLICK = auto()
    MOUSE_DOUBLE_CLICK = auto()
    MOUSE_LEFT_DOWN = auto()
    MOUSE_LEFT_UP = auto()
    MOUSE_SCROLL = auto()
    KEYBOARD_KEY = auto()
    KEYBOARD_HOTKEY = auto()


@dataclass
class ActionConfig:
    """Action dispatcher configuration.
    
    Attributes:
        enable_mouse: Enable mouse control
        enable_keyboard: Enable keyboard control
        move_duration: Mouse move animation duration
        click_interval: Minimum time between clicks
        scroll_amount: Scroll distance per gesture
        safe_mode: Enable safety features
    """
    enable_mouse: bool = True
    enable_keyboard: bool = True
    move_duration: float = 0.0  # Instant movement
    click_interval: float = 0.1
    scroll_amount: int = 3
    safe_mode: bool = True
    
    @classmethod
    def from_dict(cls, data: dict) -> ActionConfig:
        """Create config from dictionary."""
        return cls(
            enable_mouse=data.get("enable_mouse", True),
            enable_keyboard=data.get("enable_keyboard", True),
            move_duration=data.get("move_duration", 0.0),
            click_interval=data.get("click_interval", 0.1),
            scroll_amount=data.get("scroll_amount", 3),
            safe_mode=data.get("safe_mode", True),
        )


class ActionExecutor(ABC):
    """Abstract base class for action executors."""
    
    @abstractmethod
    def execute(self, **kwargs) -> bool:
        """Execute the action.
        
        Returns:
            True if action succeeded
        """
        pass


class MouseMoveExecutor(ActionExecutor):
    """Executes mouse movement."""
    
    def __init__(self, duration: float = 0.0) -> None:
        self.duration = duration
    
    def execute(self, x: int, y: int, **kwargs) -> bool:
        """Move mouse to position.
        
        Args:
            x: Screen X coordinate
            y: Screen Y coordinate
        """
        try:
            pyautogui.moveTo(x, y, duration=self.duration)
            return True
        except Exception as e:
            logger.error("Mouse move failed: %s", e)
            return False


class MouseClickExecutor(ActionExecutor):
    """Executes mouse clicks."""
    
    def __init__(self, button: str = "left") -> None:
        self.button = button
    
    def execute(self, x: Optional[int] = None, y: Optional[int] = None, **kwargs) -> bool:
        """Click at position.
        
        Args:
            x: Screen X coordinate (optional, uses current if None)
            y: Screen Y coordinate (optional)
        """
        try:
            pyautogui.click(x=x, y=y, button=self.button)
            return True
        except Exception as e:
            logger.error("Mouse click failed: %s", e)
            return False


class MouseDragExecutor(ActionExecutor):
    """Executes mouse drag operations."""
    
    def __init__(self) -> None:
        self._is_dragging = False
    
    def start_drag(self) -> bool:
        """Start drag (mouse down)."""
        try:
            pyautogui.mouseDown()
            self._is_dragging = True
            return True
        except Exception as e:
            logger.error("Mouse down failed: %s", e)
            return False
    
    def end_drag(self) -> bool:
        """End drag (mouse up)."""
        try:
            pyautogui.mouseUp()
            self._is_dragging = False
            return True
        except Exception as e:
            logger.error("Mouse up failed: %s", e)
            return False
    
    def execute(self, action: str = "start", **kwargs) -> bool:
        """Execute drag action.
        
        Args:
            action: "start" or "end"
        """
        if action == "start":
            return self.start_drag()
        elif action == "end":
            return self.end_drag()
        return False


class MouseScrollExecutor(ActionExecutor):
    """Executes mouse scroll."""
    
    def __init__(self, amount: int = 3) -> None:
        self.amount = amount
    
    def execute(self, direction: str = "up", **kwargs) -> bool:
        """Scroll in direction.
        
        Args:
            direction: "up" or "down"
        """
        try:
            clicks = self.amount if direction == "up" else -self.amount
            pyautogui.scroll(clicks)
            return True
        except Exception as e:
            logger.error("Scroll failed: %s", e)
            return False


class KeyboardExecutor(ActionExecutor):
    """Executes keyboard actions."""
    
    def execute(
        self, 
        key: Optional[str] = None, 
        hotkey: Optional[list[str]] = None, 
        **kwargs
    ) -> bool:
        """Execute keyboard action.
        
        Args:
            key: Single key to press
            hotkey: Key combination (e.g., ["ctrl", "c"])
        """
        try:
            if hotkey:
                pyautogui.hotkey(*hotkey)
            elif key:
                pyautogui.press(key)
            return True
        except Exception as e:
            logger.error("Keyboard action failed: %s", e)
            return False


class ActionDispatcher:
    """Dispatches gestures to OS actions.
    
    Manages the mapping between gestures and system actions,
    handling execution and providing feedback.
    
    Example:
        >>> dispatcher = ActionDispatcher()
        >>> dispatcher.start()
        >>> dispatcher.handle_gesture(gesture)
        >>> dispatcher.stop()
    """
    
    def __init__(self, config: Optional[ActionConfig] = None) -> None:
        """Initialize action dispatcher.
        
        Args:
            config: Action configuration
        """
        self.config = config or ActionConfig()
        self._is_running = False
        self._executors: Dict[ActionType, ActionExecutor] = {}
        self._last_action_time: Dict[ActionType, float] = {}
        self._action_count = 0
        self._drag_executor: Optional[MouseDragExecutor] = None
        
        self._setup_executors()
        
        logger.info(
            "ActionDispatcher initialized: mouse=%s, keyboard=%s, safe_mode=%s",
            self.config.enable_mouse,
            self.config.enable_keyboard,
            self.config.safe_mode
        )
    
    def _setup_executors(self) -> None:
        """Initialize action executors."""
        self._executors = {
            ActionType.MOUSE_MOVE: MouseMoveExecutor(self.config.move_duration),
            ActionType.MOUSE_LEFT_CLICK: MouseClickExecutor("left"),
            ActionType.MOUSE_RIGHT_CLICK: MouseClickExecutor("right"),
            ActionType.MOUSE_DOUBLE_CLICK: MouseClickExecutor("left"),
            ActionType.MOUSE_SCROLL: MouseScrollExecutor(self.config.scroll_amount),
            ActionType.KEYBOARD_KEY: KeyboardExecutor(),
            ActionType.KEYBOARD_HOTKEY: KeyboardExecutor(),
        }
        self._drag_executor = MouseDragExecutor()
    
    @property
    def is_running(self) -> bool:
        """Check if dispatcher is running."""
        return self._is_running
    
    @property
    def action_count(self) -> int:
        """Get total actions executed."""
        return self._action_count
    
    def start(self) -> None:
        """Start the action dispatcher."""
        if self._is_running:
            logger.warning("Dispatcher already running")
            return
        
        logger.info("Starting action dispatcher...")
        self._is_running = True
        logger.info("Action dispatcher started")
    
    def stop(self) -> None:
        """Stop the action dispatcher."""
        if not self._is_running:
            return
        
        logger.info("Stopping action dispatcher...")
        
        # Release any held mouse buttons
        if self._drag_executor and self._drag_executor._is_dragging:
            self._drag_executor.end_drag()
        
        self._is_running = False
        logger.info("Action dispatcher stopped")
    
    def handle_gesture(self, gesture: Gesture) -> bool:
        """Handle a gesture and execute corresponding action.
        
        Args:
            gesture: Detected gesture
            
        Returns:
            True if action was executed
        """
        if not self._is_running:
            return False
        
        try:
            success = self._dispatch_gesture(gesture)
            if success:
                self._action_count += 1
            return success
        except pyautogui.FailSafeException:
            logger.warning("PyAutoGUI failsafe triggered!")
            self.stop()
            return False
        except Exception as e:
            logger.error("Gesture handling error: %s", e)
            return False
    
    def _dispatch_gesture(self, gesture: Gesture) -> bool:
        """Dispatch gesture to appropriate action.
        
        Args:
            gesture: Gesture to dispatch
            
        Returns:
            True if action executed
        """
        if gesture.type == GestureType.CURSOR_MOVE:
            return self._handle_cursor_move(gesture)
        
        elif gesture.type == GestureType.LEFT_CLICK:
            return self._handle_left_click(gesture)
        
        elif gesture.type == GestureType.RIGHT_CLICK:
            return self._handle_right_click(gesture)
        
        elif gesture.type == GestureType.DRAG_START:
            return self._handle_drag_start(gesture)
        
        elif gesture.type == GestureType.DRAG_MOVE:
            return self._handle_drag_move(gesture)
        
        elif gesture.type == GestureType.DRAG_END:
            return self._handle_drag_end(gesture)
        
        elif gesture.type == GestureType.SCROLL_UP:
            return self._handle_scroll(gesture, "up")
        
        elif gesture.type == GestureType.SCROLL_DOWN:
            return self._handle_scroll(gesture, "down")
        
        return False
    
    def _handle_cursor_move(self, gesture: Gesture) -> bool:
        """Handle cursor movement."""
        if not self.config.enable_mouse:
            return False
        
        # Position should be pre-mapped to screen coordinates
        x, y = gesture.metadata.get("screen_pos", gesture.position)
        
        if isinstance(x, float):
            # Still normalized, skip (should be mapped by caller)
            return False
        
        executor = self._executors[ActionType.MOUSE_MOVE]
        return executor.execute(x=x, y=y)
    
    def _handle_left_click(self, gesture: Gesture) -> bool:
        """Handle left click."""
        if not self.config.enable_mouse:
            return False
        
        if not self._check_interval(ActionType.MOUSE_LEFT_CLICK):
            return False
        
        executor = self._executors[ActionType.MOUSE_LEFT_CLICK]
        success = executor.execute()
        
        if success:
            logger.debug("Left click executed")
        
        return success
    
    def _handle_right_click(self, gesture: Gesture) -> bool:
        """Handle right click."""
        if not self.config.enable_mouse:
            return False
        
        if not self._check_interval(ActionType.MOUSE_RIGHT_CLICK):
            return False
        
        executor = self._executors[ActionType.MOUSE_RIGHT_CLICK]
        success = executor.execute()
        
        if success:
            logger.debug("Right click executed")
        
        return success
    
    def _handle_drag_start(self, gesture: Gesture) -> bool:
        """Handle drag start."""
        if not self.config.enable_mouse or not self._drag_executor:
            return False
        
        success = self._drag_executor.start_drag()
        
        if success:
            logger.debug("Drag started")
        
        return success
    
    def _handle_drag_move(self, gesture: Gesture) -> bool:
        """Handle drag movement."""
        # Cursor movement during drag is handled by cursor_move
        return True
    
    def _handle_drag_end(self, gesture: Gesture) -> bool:
        """Handle drag end."""
        if not self._drag_executor:
            return False
        
        success = self._drag_executor.end_drag()
        
        if success:
            logger.debug("Drag ended")
        
        return success
    
    def _handle_scroll(self, gesture: Gesture, direction: str) -> bool:
        """Handle scroll gesture."""
        if not self.config.enable_mouse:
            return False
        
        executor = self._executors[ActionType.MOUSE_SCROLL]
        return executor.execute(direction=direction)
    
    def _check_interval(self, action_type: ActionType) -> bool:
        """Check if enough time has passed since last action.
        
        Args:
            action_type: Type of action
            
        Returns:
            True if action can proceed
        """
        current_time = time.time()
        last_time = self._last_action_time.get(action_type, 0)
        
        if current_time - last_time < self.config.click_interval:
            return False
        
        self._last_action_time[action_type] = current_time
        return True
    
    def move_cursor(self, x: int, y: int) -> bool:
        """Directly move cursor to position.
        
        Args:
            x: Screen X coordinate
            y: Screen Y coordinate
            
        Returns:
            True if successful
        """
        if not self._is_running or not self.config.enable_mouse:
            return False
        
        try:
            pyautogui.moveTo(x, y, duration=self.config.move_duration)
            return True
        except Exception as e:
            logger.error("Direct cursor move failed: %s", e)
            return False
    
    def click(self, button: str = "left") -> bool:
        """Execute click at current position.
        
        Args:
            button: "left" or "right"
            
        Returns:
            True if successful
        """
        if not self._is_running or not self.config.enable_mouse:
            return False
        
        try:
            pyautogui.click(button=button)
            return True
        except Exception as e:
            logger.error("Direct click failed: %s", e)
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a keyboard key.
        
        Args:
            key: Key name
            
        Returns:
            True if successful
        """
        if not self._is_running or not self.config.enable_keyboard:
            return False
        
        executor = self._executors[ActionType.KEYBOARD_KEY]
        return executor.execute(key=key)
    
    def hotkey(self, *keys: str) -> bool:
        """Execute keyboard hotkey.
        
        Args:
            keys: Keys to press together
            
        Returns:
            True if successful
        """
        if not self._is_running or not self.config.enable_keyboard:
            return False
        
        executor = self._executors[ActionType.KEYBOARD_HOTKEY]
        return executor.execute(hotkey=list(keys))
    
    def __enter__(self) -> ActionDispatcher:
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
