"""
REST API Server

Provides HTTP endpoints for controlling Spatial Touch from external clients.
Built with FastAPI for high performance and automatic OpenAPI documentation.
"""

from __future__ import annotations

import asyncio
import threading
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for API
# ============================================================================

class CameraSettings(BaseModel):
    """Camera configuration model."""
    device_index: int = Field(0, ge=0, description="Camera device index")
    resolution: List[int] = Field([1280, 720], description="Resolution [width, height]")
    fps: int = Field(30, ge=1, le=120, description="Frames per second")
    auto_reconnect: bool = Field(True, description="Auto-reconnect on disconnect")
    reconnect_delay: float = Field(2.0, ge=0.1, le=10.0, description="Reconnect delay in seconds")
    warmup_frames: int = Field(10, ge=0, le=100, description="Warmup frames to skip")


class TrackingSettings(BaseModel):
    """Hand tracking configuration model."""
    max_hands: int = Field(1, ge=1, le=2, description="Maximum hands to track")
    min_detection_confidence: float = Field(0.7, ge=0.1, le=1.0, description="Detection confidence threshold")
    min_tracking_confidence: float = Field(0.5, ge=0.1, le=1.0, description="Tracking confidence threshold")
    model_complexity: int = Field(1, ge=0, le=2, description="Model complexity (0=lite, 1=full, 2=heavy)")
    smoothing_factor: float = Field(0.4, ge=0.0, le=1.0, description="Smoothing factor for landmarks")


class GestureSettings(BaseModel):
    """Gesture detection configuration model."""
    pinch_threshold: float = Field(0.05, ge=0.01, le=0.2, description="Pinch detection threshold")
    debounce_ms: int = Field(200, ge=50, le=1000, description="Debounce time in milliseconds")
    hold_time_ms: int = Field(300, ge=100, le=2000, description="Hold time for long press")
    click_release_ms: int = Field(200, ge=50, le=500, description="Max release time for click")
    velocity_threshold: float = Field(0.01, ge=0.0, le=0.1, description="Velocity threshold for swipe")


class CursorSettings(BaseModel):
    """Cursor/zone mapping configuration model."""
    sensitivity: float = Field(1.0, ge=0.1, le=5.0, description="Cursor sensitivity multiplier")
    dead_zone: float = Field(0.02, ge=0.0, le=0.2, description="Dead zone radius")
    invert_x: bool = Field(True, description="Invert X axis (mirror mode)")
    invert_y: bool = Field(False, description="Invert Y axis")
    margin: int = Field(10, ge=0, le=100, description="Screen edge margin in pixels")
    smoothing: float = Field(0.0, ge=0.0, le=1.0, description="Additional cursor smoothing")


class ActionSettings(BaseModel):
    """Action dispatcher configuration model."""
    enable_mouse: bool = Field(True, description="Enable mouse control")
    enable_keyboard: bool = Field(True, description="Enable keyboard shortcuts")
    move_duration: float = Field(0.0, ge=0.0, le=1.0, description="Mouse movement duration")
    click_interval: float = Field(0.1, ge=0.0, le=1.0, description="Interval between clicks")
    scroll_amount: int = Field(3, ge=1, le=20, description="Scroll amount per gesture")
    safe_mode: bool = Field(True, description="Safe mode (limits cursor speed)")


class SystemSettings(BaseModel):
    """System configuration model."""
    log_level: str = Field("INFO", description="Logging level")
    debug_mode: bool = Field(False, description="Enable debug mode")
    idle_fps: int = Field(5, ge=1, le=30, description="FPS when idle")
    active_fps: int = Field(30, ge=10, le=120, description="FPS when active")
    run_on_startup: bool = Field(False, description="Run on Windows startup")
    show_tray_icon: bool = Field(True, description="Show system tray icon")


class AllSettings(BaseModel):
    """Complete application settings."""
    camera: CameraSettings = Field(default_factory=CameraSettings)
    tracking: TrackingSettings = Field(default_factory=TrackingSettings)
    gestures: GestureSettings = Field(default_factory=GestureSettings)
    cursor: CursorSettings = Field(default_factory=CursorSettings)
    actions: ActionSettings = Field(default_factory=ActionSettings)
    system: SystemSettings = Field(default_factory=SystemSettings)


class GestureBinding(BaseModel):
    """Custom gesture binding model."""
    gesture: str = Field(..., description="Gesture name (pinch, double_tap, swipe_left, etc.)")
    action: str = Field(..., description="Action type (key, mouse, command)")
    value: str = Field(..., description="Action value (key combo, mouse action, command)")
    enabled: bool = Field(True, description="Whether binding is enabled")


class CameraInfo(BaseModel):
    """Camera device information."""
    index: int
    name: str
    resolutions: List[List[int]]
    is_current: bool


class AppStatus(BaseModel):
    """Application status."""
    running: bool
    paused: bool
    tracking_active: bool
    camera_connected: bool
    fps_actual: float
    frame_count: int
    gestures_detected: int


# ============================================================================
# API Server
# ============================================================================

def create_api_app(controller=None) -> FastAPI:
    """Create FastAPI application instance.
    
    Args:
        controller: SpatialTouchController instance (optional, can be set later)
        
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Spatial Touch API",
        description="REST API for controlling Spatial Touch hand gesture application",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware for Flutter app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store controller reference
    app.state.controller = controller
    app.state.config_path = None
    app.state.gestures_path = None
    
    # WebSocket connections for real-time updates
    app.state.ws_connections: List[WebSocket] = []
    
    # ========================================================================
    # Settings Endpoints
    # ========================================================================
    
    @app.get("/api/settings", response_model=AllSettings, tags=["Settings"])
    async def get_all_settings():
        """Get all application settings."""
        try:
            config_path = app.state.config_path or _get_default_config_path()
            settings = _load_settings(config_path)
            return AllSettings(**settings)
        except Exception as e:
            logger.error("Failed to load settings: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/api/settings", response_model=AllSettings, tags=["Settings"])
    async def update_all_settings(settings: AllSettings):
        """Update all application settings."""
        try:
            config_path = app.state.config_path or _get_default_config_path()
            _save_settings(config_path, settings.model_dump())
            
            # Notify WebSocket clients
            await _broadcast_update(app, "settings_updated", settings.model_dump())
            
            # Reload controller if running
            if app.state.controller and app.state.controller.is_running:
                await _reload_controller_config(app.state.controller, settings)
            
            return settings
        except Exception as e:
            logger.error("Failed to save settings: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/settings/camera", response_model=CameraSettings, tags=["Settings"])
    async def get_camera_settings():
        """Get camera settings."""
        settings = await get_all_settings()
        return settings.camera
    
    @app.put("/api/settings/camera", response_model=CameraSettings, tags=["Settings"])
    async def update_camera_settings(camera: CameraSettings):
        """Update camera settings."""
        settings = await get_all_settings()
        settings.camera = camera
        await update_all_settings(settings)
        return camera
    
    @app.get("/api/settings/tracking", response_model=TrackingSettings, tags=["Settings"])
    async def get_tracking_settings():
        """Get tracking settings."""
        settings = await get_all_settings()
        return settings.tracking
    
    @app.put("/api/settings/tracking", response_model=TrackingSettings, tags=["Settings"])
    async def update_tracking_settings(tracking: TrackingSettings):
        """Update tracking settings."""
        settings = await get_all_settings()
        settings.tracking = tracking
        await update_all_settings(settings)
        return tracking
    
    @app.get("/api/settings/gestures", response_model=GestureSettings, tags=["Settings"])
    async def get_gesture_settings():
        """Get gesture detection settings."""
        settings = await get_all_settings()
        return settings.gestures
    
    @app.put("/api/settings/gestures", response_model=GestureSettings, tags=["Settings"])
    async def update_gesture_settings(gestures: GestureSettings):
        """Update gesture detection settings."""
        settings = await get_all_settings()
        settings.gestures = gestures
        await update_all_settings(settings)
        return gestures
    
    @app.get("/api/settings/cursor", response_model=CursorSettings, tags=["Settings"])
    async def get_cursor_settings():
        """Get cursor settings."""
        settings = await get_all_settings()
        return settings.cursor
    
    @app.put("/api/settings/cursor", response_model=CursorSettings, tags=["Settings"])
    async def update_cursor_settings(cursor: CursorSettings):
        """Update cursor settings."""
        settings = await get_all_settings()
        settings.cursor = cursor
        await update_all_settings(settings)
        return cursor
    
    @app.get("/api/settings/actions", response_model=ActionSettings, tags=["Settings"])
    async def get_action_settings():
        """Get action dispatcher settings."""
        settings = await get_all_settings()
        return settings.actions
    
    @app.put("/api/settings/actions", response_model=ActionSettings, tags=["Settings"])
    async def update_action_settings(actions: ActionSettings):
        """Update action dispatcher settings."""
        settings = await get_all_settings()
        settings.actions = actions
        await update_all_settings(settings)
        return actions
    
    @app.get("/api/settings/system", response_model=SystemSettings, tags=["Settings"])
    async def get_system_settings():
        """Get system settings."""
        settings = await get_all_settings()
        return settings.system
    
    @app.put("/api/settings/system", response_model=SystemSettings, tags=["Settings"])
    async def update_system_settings(system: SystemSettings):
        """Update system settings."""
        settings = await get_all_settings()
        settings.system = system
        await update_all_settings(settings)
        return system
    
    # ========================================================================
    # Gesture Bindings Endpoints
    # ========================================================================
    
    @app.get("/api/bindings", response_model=List[GestureBinding], tags=["Bindings"])
    async def get_gesture_bindings():
        """Get all gesture bindings."""
        try:
            gestures_path = app.state.gestures_path or _get_default_gestures_path()
            bindings = _load_gesture_bindings(gestures_path)
            return bindings
        except Exception as e:
            logger.error("Failed to load bindings: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/api/bindings", response_model=List[GestureBinding], tags=["Bindings"])
    async def update_gesture_bindings(bindings: List[GestureBinding]):
        """Update all gesture bindings."""
        try:
            gestures_path = app.state.gestures_path or _get_default_gestures_path()
            _save_gesture_bindings(gestures_path, bindings)
            await _broadcast_update(app, "bindings_updated", [b.model_dump() for b in bindings])
            return bindings
        except Exception as e:
            logger.error("Failed to save bindings: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/bindings", response_model=GestureBinding, tags=["Bindings"])
    async def add_gesture_binding(binding: GestureBinding):
        """Add a new gesture binding."""
        bindings = await get_gesture_bindings()
        bindings.append(binding)
        await update_gesture_bindings(bindings)
        return binding
    
    @app.delete("/api/bindings/{gesture}", tags=["Bindings"])
    async def delete_gesture_binding(gesture: str):
        """Delete a gesture binding."""
        bindings = await get_gesture_bindings()
        bindings = [b for b in bindings if b.gesture != gesture]
        await update_gesture_bindings(bindings)
        return {"status": "deleted", "gesture": gesture}
    
    # ========================================================================
    # Camera Endpoints
    # ========================================================================
    
    @app.get("/api/cameras", response_model=List[CameraInfo], tags=["Camera"])
    async def list_cameras():
        """List available cameras."""
        try:
            cameras = _enumerate_cameras()
            return cameras
        except Exception as e:
            logger.error("Failed to enumerate cameras: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/cameras/select/{index}", tags=["Camera"])
    async def select_camera(index: int):
        """Select a camera by index."""
        settings = await get_all_settings()
        settings.camera.device_index = index
        await update_all_settings(settings)
        return {"status": "selected", "index": index}
    
    @app.post("/api/cameras/test/{index}", tags=["Camera"])
    async def test_camera(index: int):
        """Test if a camera is accessible."""
        try:
            import cv2
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            success = cap.isOpened()
            if success:
                ret, _ = cap.read()
                success = ret
            cap.release()
            return {"index": index, "accessible": success}
        except Exception as e:
            return {"index": index, "accessible": False, "error": str(e)}
    
    # ========================================================================
    # Control Endpoints
    # ========================================================================
    
    @app.get("/api/status", response_model=AppStatus, tags=["Control"])
    async def get_status():
        """Get current application status."""
        controller = app.state.controller
        if controller:
            return AppStatus(
                running=controller.is_running,
                paused=controller.is_paused,
                tracking_active=controller._tracker is not None and controller._tracker.is_running if hasattr(controller, '_tracker') and controller._tracker else False,
                camera_connected=controller._camera is not None and controller._camera.state.name == "CONNECTED" if hasattr(controller, '_camera') and controller._camera else False,
                fps_actual=controller._camera.fps_actual if hasattr(controller, '_camera') and controller._camera and hasattr(controller._camera, 'fps_actual') else 0.0,
                frame_count=controller.frame_count,
                gestures_detected=0  # TODO: Add gesture counter
            )
        return AppStatus(
            running=False,
            paused=False,
            tracking_active=False,
            camera_connected=False,
            fps_actual=0.0,
            frame_count=0,
            gestures_detected=0
        )
    
    @app.post("/api/control/start", tags=["Control"])
    async def start_tracking():
        """Start gesture tracking."""
        controller = app.state.controller
        if controller and not controller.is_running:
            # Start in non-blocking mode
            threading.Thread(target=controller.start, kwargs={"blocking": True}, daemon=True).start()
            await asyncio.sleep(0.5)  # Wait for startup
            await _broadcast_update(app, "status_changed", {"running": True})
            return {"status": "started"}
        return {"status": "already_running"}
    
    @app.post("/api/control/stop", tags=["Control"])
    async def stop_tracking():
        """Stop gesture tracking."""
        controller = app.state.controller
        if controller and controller.is_running:
            controller.stop()
            await _broadcast_update(app, "status_changed", {"running": False})
            return {"status": "stopped"}
        return {"status": "not_running"}
    
    @app.post("/api/control/pause", tags=["Control"])
    async def pause_tracking():
        """Pause gesture tracking."""
        controller = app.state.controller
        if controller:
            controller.pause()
            await _broadcast_update(app, "status_changed", {"paused": True})
            return {"status": "paused"}
        raise HTTPException(status_code=400, detail="Controller not initialized")
    
    @app.post("/api/control/resume", tags=["Control"])
    async def resume_tracking():
        """Resume gesture tracking."""
        controller = app.state.controller
        if controller:
            controller.resume()
            await _broadcast_update(app, "status_changed", {"paused": False})
            return {"status": "resumed"}
        raise HTTPException(status_code=400, detail="Controller not initialized")
    
    @app.post("/api/control/toggle", tags=["Control"])
    async def toggle_tracking():
        """Toggle pause state."""
        controller = app.state.controller
        if controller:
            paused = controller.toggle_pause()
            await _broadcast_update(app, "status_changed", {"paused": paused})
            return {"paused": paused}
        raise HTTPException(status_code=400, detail="Controller not initialized")
    
    # ========================================================================
    # WebSocket for Real-time Updates
    # ========================================================================
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket for real-time status updates."""
        await websocket.accept()
        app.state.ws_connections.append(websocket)
        logger.info("WebSocket client connected")
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                # Handle ping/pong for keep-alive
                if data == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        finally:
            if websocket in app.state.ws_connections:
                app.state.ws_connections.remove(websocket)
    
    return app


# ============================================================================
# Helper Functions
# ============================================================================

def _get_default_config_path() -> Path:
    """Get default config file path."""
    return Path(__file__).parent.parent.parent.parent / "config" / "settings.json"


def _get_default_gestures_path() -> Path:
    """Get default gestures file path."""
    return Path(__file__).parent.parent.parent.parent / "config" / "gestures.json"


def _load_settings(path: Path) -> dict:
    """Load settings from JSON file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_settings(path: Path, settings: dict) -> None:
    """Save settings to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def _load_gesture_bindings(path: Path) -> List[GestureBinding]:
    """Load gesture bindings from JSON file."""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    bindings = []
    for gesture, actions in data.get("gestures", {}).items():
        for action_type, value in actions.items():
            if action_type in ("key", "mouse", "command"):
                bindings.append(GestureBinding(
                    gesture=gesture,
                    action=action_type,
                    value=value if isinstance(value, str) else json.dumps(value),
                    enabled=True
                ))
    return bindings


def _save_gesture_bindings(path: Path, bindings: List[GestureBinding]) -> None:
    """Save gesture bindings to JSON file."""
    # Load existing structure
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"gestures": {}, "defaults": {}}
    
    # Update gestures
    data["gestures"] = {}
    for binding in bindings:
        if binding.gesture not in data["gestures"]:
            data["gestures"][binding.gesture] = {}
        data["gestures"][binding.gesture][binding.action] = binding.value
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _enumerate_cameras() -> List[CameraInfo]:
    """Enumerate available camera devices."""
    import cv2
    cameras = []
    
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            # Get camera name (Windows-specific)
            name = f"Camera {i}"
            
            # Common resolutions to test
            resolutions = []
            test_res = [(640, 480), (1280, 720), (1920, 1080)]
            for w, h in test_res:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if [actual_w, actual_h] not in resolutions:
                    resolutions.append([actual_w, actual_h])
            
            cameras.append(CameraInfo(
                index=i,
                name=name,
                resolutions=resolutions,
                is_current=False  # Will be updated by caller
            ))
            cap.release()
    
    return cameras


async def _broadcast_update(app: FastAPI, event: str, data: Any) -> None:
    """Broadcast update to all WebSocket clients."""
    message = json.dumps({"event": event, "data": data})
    disconnected = []
    
    for ws in app.state.ws_connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in app.state.ws_connections:
            app.state.ws_connections.remove(ws)


async def _reload_controller_config(controller, settings: AllSettings) -> None:
    """Reload controller configuration (hot reload)."""
    # This would trigger a config reload in the controller
    # For now, just log that we would reload
    logger.info("Config reload requested - restart may be required for some changes")


# ============================================================================
# API Server Class
# ============================================================================

@dataclass
class APIServerConfig:
    """API server configuration."""
    host: str = "127.0.0.1"
    port: int = 8765
    reload: bool = False
    log_level: str = "info"


class APIServer:
    """Manages the REST API server.
    
    Runs the FastAPI server in a background thread to allow
    concurrent operation with the main gesture processing loop.
    
    Example:
        >>> server = APIServer(controller)
        >>> server.start()
        >>> # Server running at http://localhost:8765
        >>> server.stop()
    """
    
    def __init__(
        self,
        controller=None,
        config: Optional[APIServerConfig] = None,
        config_path: Optional[Path] = None,
        gestures_path: Optional[Path] = None
    ) -> None:
        """Initialize API server.
        
        Args:
            controller: SpatialTouchController instance
            config: Server configuration
            config_path: Path to settings.json
            gestures_path: Path to gestures.json
        """
        self.config = config or APIServerConfig()
        self.app = create_api_app(controller)
        self.app.state.config_path = config_path
        self.app.state.gestures_path = gestures_path
        
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    def set_controller(self, controller) -> None:
        """Set the controller reference.
        
        Args:
            controller: SpatialTouchController instance
        """
        self.app.state.controller = controller
    
    def start(self) -> None:
        """Start the API server in a background thread."""
        if self._running:
            logger.warning("API server already running")
            return
        
        logger.info("Starting API server on %s:%d", self.config.host, self.config.port)
        
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
            loop="asyncio"
        )
        self._server = uvicorn.Server(config)
        
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        self._running = True
        
        logger.info("API server started")
    
    def _run_server(self) -> None:
        """Run the server (called in background thread)."""
        asyncio.run(self._server.serve())
    
    def stop(self) -> None:
        """Stop the API server."""
        if not self._running:
            return
        
        logger.info("Stopping API server...")
        
        if self._server:
            self._server.should_exit = True
        
        self._running = False
        logger.info("API server stopped")
