# Configuration Guide

Spatial Touch uses JSON configuration files for customization.

## Configuration Files

| File | Purpose |
|------|---------|
| `config/settings.json` | Main application settings |
| `config/gestures.json` | Gesture definitions and mappings |

## Settings Reference

### Camera Settings

```json
{
  "camera": {
    "device_index": 0,
    "resolution": [1280, 720],
    "fps": 30,
    "auto_reconnect": true,
    "reconnect_delay": 2.0,
    "warmup_frames": 10
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `device_index` | int | 0 | Camera device index (0 = default) |
| `resolution` | [int, int] | [1280, 720] | Capture resolution |
| `fps` | int | 30 | Target frame rate |
| `auto_reconnect` | bool | true | Reconnect on disconnect |
| `reconnect_delay` | float | 2.0 | Seconds between reconnect attempts |
| `warmup_frames` | int | 10 | Frames to skip during init |

### Tracking Settings

```json
{
  "tracking": {
    "max_hands": 1,
    "min_detection_confidence": 0.7,
    "min_tracking_confidence": 0.5,
    "model_complexity": 1,
    "smoothing_factor": 0.4,
    "static_image_mode": false
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `max_hands` | int | 1 | Maximum hands to track |
| `min_detection_confidence` | float | 0.7 | Minimum detection confidence (0-1) |
| `min_tracking_confidence` | float | 0.5 | Minimum tracking confidence (0-1) |
| `model_complexity` | int | 1 | Model complexity (0=lite, 1=full) |
| `smoothing_factor` | float | 0.4 | Landmark smoothing (0=smooth, 1=responsive) |
| `static_image_mode` | bool | false | Optimize for video (false) or images (true) |

### Gesture Settings

```json
{
  "gestures": {
    "pinch_threshold": 0.05,
    "debounce_ms": 200,
    "hold_time_ms": 300,
    "click_release_ms": 200,
    "velocity_threshold": 0.01
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `pinch_threshold` | float | 0.05 | Pinch trigger distance (normalized) |
| `debounce_ms` | int | 200 | Minimum time between gestures |
| `hold_time_ms` | int | 300 | Time to trigger hold/drag |
| `click_release_ms` | int | 200 | Max time for click (vs hold) |
| `velocity_threshold` | float | 0.01 | Minimum movement for cursor update |

### Cursor Settings

```json
{
  "cursor": {
    "screen_width": 1920,
    "screen_height": 1080,
    "sensitivity": 1.0,
    "dead_zone": 0.02,
    "invert_x": true,
    "invert_y": false,
    "margin": 10,
    "smoothing": 0.0
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `screen_width` | int | 1920 | Screen width (auto-detected) |
| `screen_height` | int | 1080 | Screen height (auto-detected) |
| `sensitivity` | float | 1.0 | Cursor movement multiplier |
| `dead_zone` | float | 0.02 | Ignore movements below this |
| `invert_x` | bool | true | Mirror horizontal movement |
| `invert_y` | bool | false | Invert vertical movement |
| `margin` | int | 10 | Screen edge margin in pixels |
| `smoothing` | float | 0.0 | Additional position smoothing |

### Action Settings

```json
{
  "actions": {
    "enable_mouse": true,
    "enable_keyboard": true,
    "move_duration": 0.0,
    "click_interval": 0.1,
    "scroll_amount": 3,
    "safe_mode": true
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enable_mouse` | bool | true | Enable mouse control |
| `enable_keyboard` | bool | true | Enable keyboard control |
| `move_duration` | float | 0.0 | Mouse move animation (0=instant) |
| `click_interval` | float | 0.1 | Minimum click interval |
| `scroll_amount` | int | 3 | Scroll lines per gesture |
| `safe_mode` | bool | true | Enable PyAutoGUI failsafe |

### System Settings

```json
{
  "system": {
    "log_level": "INFO",
    "log_file": "logs/spatial_touch.log",
    "debug_mode": false,
    "idle_fps": 5,
    "active_fps": 30,
    "idle_timeout_frames": 30,
    "run_on_startup": false,
    "show_tray_icon": true
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `log_level` | string | "INFO" | Logging level |
| `log_file` | string | null | Log file path (null for no file) |
| `debug_mode` | bool | false | Enable debug features |
| `idle_fps` | int | 5 | FPS when no hand detected |
| `active_fps` | int | 30 | FPS during interaction |
| `idle_timeout_frames` | int | 30 | Frames before idle mode |
| `run_on_startup` | bool | false | Start with Windows |
| `show_tray_icon` | bool | true | Show system tray icon |

---

## Environment Variables

Override settings with environment variables:

```powershell
$env:SPATIAL_TOUCH_DEBUG = "1"
$env:SPATIAL_TOUCH_CAMERA = "1"
$env:SPATIAL_TOUCH_LOG_LEVEL = "DEBUG"
```

---

## Profiles

Create different profiles in `config/gestures.json`:

```json
{
  "profiles": {
    "default": {
      "name": "Default Profile",
      "gestures": ["cursor_move", "left_click", "right_click", "drag"]
    },
    "presentation": {
      "name": "Presentation Mode",
      "gestures": ["cursor_move", "left_click"],
      "overrides": {
        "cursor": {
          "sensitivity": 1.5
        }
      }
    }
  }
}
```

Switch profiles via command line:

```powershell
python -m spatial_touch --profile presentation
```

---

## Hot Reload

Configuration changes are not hot-reloaded by default. Restart Spatial Touch to apply changes:

```powershell
# Stop with Ctrl+C, then restart
python -m spatial_touch
```

---

## Example Configurations

### High Precision (Drawing)

```json
{
  "cursor": {
    "sensitivity": 0.7,
    "dead_zone": 0.01,
    "smoothing": 0.3
  },
  "tracking": {
    "smoothing_factor": 0.3
  }
}
```

### Fast Responsiveness (Gaming)

```json
{
  "cursor": {
    "sensitivity": 1.5,
    "dead_zone": 0.005,
    "smoothing": 0.0
  },
  "tracking": {
    "smoothing_factor": 0.6
  }
}
```

### Accessibility (Reduced Motion)

```json
{
  "cursor": {
    "sensitivity": 0.5,
    "dead_zone": 0.03,
    "smoothing": 0.5
  },
  "gestures": {
    "hold_time_ms": 500,
    "debounce_ms": 300
  }
}
```
