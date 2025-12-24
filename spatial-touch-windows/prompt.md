# 🤖 Spatial Touch - Copilot Development Prompt

> **Copy this entire file into GitHub Copilot or any AI assistant to generate the codebase.**

---

## System Role

You are an expert Windows system developer and computer vision engineer with deep expertise in:
- Real-time computer vision pipelines
- Hand tracking and gesture recognition
- Windows system programming
- Production-grade Python architecture
- Accessibility software development

---

## Project Overview

Build a Windows background application called **"Spatial Touch"** that enables touchless computer control using hand gestures captured via the laptop webcam. This is an open-source project targeting Microsoft/Google-level code quality.

---

## Strict Requirements

### Platform & Environment
- **Target OS:** Windows 10 / 11 (64-bit)
- **Language:** Python 3.11+
- **Runtime:** Background process (no visible window during operation)
- **Input:** Standard laptop webcam (720p minimum)
- **Output:** Real OS-level mouse and keyboard events

### Code Quality Standards
- Follow PEP 8 and PEP 257 (docstrings)
- Type hints on all functions
- Comprehensive error handling
- Logging at all critical points
- Unit test ready architecture
- Clean separation of concerns

---

## Core Features to Implement

### Phase 1: Foundation (MVP)
1. **Camera Management** (`camera.py`)
   - Webcam capture using OpenCV
   - Frame rate control (target: 30 FPS)
   - Auto-reconnect on camera disconnect
   - Resource cleanup on exit

2. **Hand Tracking** (`hand_tracker.py`)
   - MediaPipe Hands integration (21 landmarks)
   - Multi-hand support (primary hand selection)
   - Landmark smoothing (exponential moving average)
   - Confidence thresholding

3. **Gesture Detection** (`gesture_engine.py`)
   - Pinch detection (thumb-to-finger distance)
   - Gesture state machine (idle → active → completed)
   - Temporal debouncing (prevent false positives)
   - Gesture velocity tracking

4. **Cursor Control** (`action_dispatcher.py`)
   - Screen coordinate mapping
   - Smooth cursor movement
   - Left/right click injection
   - Drag and drop support

5. **Main Controller** (`main.py`)
   - Event loop orchestration
   - Graceful shutdown handling
   - Performance monitoring
   - Configuration loading

### Phase 2: Polish
6. **Zone Mapping** (`zone_mapper.py`)
   - Screen region detection
   - Edge gestures (swipe from edges)
   - Dead zone configuration

7. **Configuration System** (`config/`)
   - JSON-based settings
   - Hot-reload support
   - Per-application profiles (future)

8. **System Integration**
   - System tray icon
   - Auto-start on login
   - Global hotkey to toggle

---

## Architecture Rules

### File Structure
```
spatial-touch-windows/
├── src/
│   └── spatial_touch/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── camera.py
│       │   ├── hand_tracker.py
│       │   ├── gesture_engine.py
│       │   ├── zone_mapper.py
│       │   └── action_dispatcher.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── smoothing.py
│       │   ├── logger.py
│       │   ├── math_helpers.py
│       │   └── performance.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── config_manager.py
│       └── main.py
├── config/
│   ├── gestures.json
│   ├── settings.json
│   └── profiles/
├── tests/
│   ├── __init__.py
│   ├── test_gesture_engine.py
│   └── test_smoothing.py
├── docs/
├── scripts/
│   ├── build.py
│   └── install_startup.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── LICENSE
```

### Design Patterns to Use
- **Strategy Pattern:** For swappable gesture detectors
- **Observer Pattern:** For gesture event callbacks
- **State Machine:** For gesture lifecycle
- **Singleton:** For configuration manager
- **Factory:** For action creators

### Class Design Guidelines
```python
# Example: All core classes should follow this pattern
class GestureEngine:
    """Detects gestures from hand landmarks.
    
    Attributes:
        config: Gesture configuration parameters
        callbacks: Registered gesture event handlers
    
    Example:
        engine = GestureEngine(config)
        engine.on_gesture(GestureType.PINCH, handle_pinch)
        engine.process(landmarks)
    """
    
    def __init__(self, config: GestureConfig) -> None:
        ...
    
    def process(self, landmarks: HandLandmarks) -> Optional[Gesture]:
        ...
    
    def on_gesture(self, gesture_type: GestureType, callback: Callable) -> None:
        ...
```

---

## Implementation Details

### Smoothing Algorithm
```python
# Exponential Moving Average (EMA)
smoothed = alpha * current + (1 - alpha) * previous
# Alpha: 0.3–0.5 for responsive yet stable cursor
```

### Pinch Detection
```python
# Euclidean distance between fingertips
distance = sqrt((x2-x1)² + (y2-y1)² + (z2-z1)²)
is_pinch = distance < PINCH_THRESHOLD  # ~0.05 normalized
```

### Coordinate Mapping
```python
# Map normalized camera coords (0–1) to screen pixels
screen_x = int(hand_x * screen_width)
screen_y = int(hand_y * screen_height)
# Apply dead zones and boundaries
```

### Performance Targets
| Metric | Target | Critical |
|--------|--------|----------|
| Latency | < 50ms | < 100ms |
| Frame Rate | 30 FPS | 20 FPS |
| CPU (active) | < 10% | < 20% |
| CPU (idle) | < 2% | < 5% |
| Memory | < 200MB | < 500MB |

---

## Configuration Schema

### `settings.json`
```json
{
  "camera": {
    "device_index": 0,
    "resolution": [1280, 720],
    "fps": 30
  },
  "tracking": {
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.5,
    "max_hands": 1
  },
  "cursor": {
    "smoothing_factor": 0.4,
    "sensitivity": 1.0,
    "dead_zone": 0.02
  },
  "gestures": {
    "pinch_threshold": 0.05,
    "debounce_ms": 150,
    "hold_time_ms": 300
  },
  "system": {
    "run_on_startup": false,
    "show_tray_icon": true,
    "log_level": "INFO"
  }
}
```

### `gestures.json`
```json
{
  "gestures": [
    {
      "id": "left_click",
      "trigger": "thumb_index_pinch",
      "action": "mouse_left_click",
      "debounce_ms": 200
    },
    {
      "id": "right_click", 
      "trigger": "thumb_middle_pinch",
      "action": "mouse_right_click",
      "debounce_ms": 200
    },
    {
      "id": "drag",
      "trigger": "thumb_index_pinch_hold",
      "action": "mouse_drag",
      "hold_time_ms": 300
    }
  ]
}
```

---

## Critical Constraints

### DO:
✅ Use type hints everywhere
✅ Add docstrings to all public methods
✅ Implement proper resource cleanup
✅ Use context managers for camera
✅ Log all errors with stack traces
✅ Make all thresholds configurable
✅ Support graceful degradation

### DO NOT:
❌ Use Flutter or any GUI framework in core
❌ Use cloud services or APIs
❌ Store or transmit camera frames
❌ Block the main thread
❌ Use global variables
❌ Hardcode thresholds or paths

---

## Output Expectations

When generating code:
1. Provide complete, runnable Python files
2. Include comprehensive docstrings
3. Add inline comments for complex logic
4. Follow the exact file structure above
5. Ensure all imports are explicit
6. Make code PyInstaller-compatible

---

## Testing Requirements

Each module should have corresponding tests:
```python
# test_gesture_engine.py
def test_pinch_detection():
    """Verify pinch is detected when fingers are close."""
    ...

def test_debounce_prevents_double_click():
    """Verify rapid pinches don't trigger multiple clicks."""
    ...
```

---

## Example Usage (Target API)

```python
from spatial_touch import SpatialTouchController

# Simple usage
controller = SpatialTouchController()
controller.start()

# Advanced usage with callbacks
controller = SpatialTouchController(config_path="config/settings.json")
controller.on_gesture("left_click", lambda: print("Clicked!"))
controller.on_error(lambda e: logger.error(e))
controller.start(blocking=True)
```

---

**Focus on correctness, performance, and clean architecture.**
**This is open-source software intended for production use.**
