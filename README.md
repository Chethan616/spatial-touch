# Spatial Touch - Complete System

A professional, open-source Windows application for touchless computer control using hand gestures via webcam.

## 📁 Project Structure

``` 
ST/
├── spatial-touch-windows/     # Python Backend
│   ├── src/spatial_touch/     # Core application
│   │   ├── api/              # REST API server
│   │   ├── core/             # Camera, tracking, gestures
│   │   └── utils/            # Helpers, logging
│   ├── config/               # JSON configuration
│   └── venv/                 # Python virtual environment
│
├── spatial-touch-app/         # Flutter Settings App
│   └── lib/src/
│       ├── core/             # Theme, services, config
│       └── features/         # UI screens
│
├── start-spatial-touch.bat    # Windows launcher
└── Start-SpatialTouch.ps1     # PowerShell launcher
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - For the gesture tracking backend
- **Flutter 3.6+** - For the settings app
- **Webcam** - Any USB or built-in camera

### Installation

1. **Setup Python Backend:**
   ```powershell
   cd spatial-touch-windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -e .
   ```

2. **Setup Flutter App:**
   ```powershell
   cd spatial-touch-app
   flutter pub get
   ```

### Running

**Option 1: Use the launcher script**
```powershell
.\Start-SpatialTouch.ps1
```

**Option 2: Run manually**

Terminal 1 - Start Python backend with API:
```powershell
cd spatial-touch-windows
.\venv\Scripts\Activate.ps1
python -m spatial_touch --api
```

Terminal 2 - Start Flutter app:
```powershell
cd spatial-touch-app
flutter run -d windows
```

## 🎯 Features

### Python Backend
- 📷 Real-time hand tracking with MediaPipe
- 🖱️ Mouse cursor control via gestures
- ⌨️ Custom keyboard shortcuts
- 🔌 REST API for external control
- 📊 Performance monitoring

### Flutter Settings App
- 🎛️ Complete settings control
- 📷 Camera device selection
- 🎚️ Sensitivity & threshold sliders
- ⌨️ Custom keybind editor
- 🌙 Dark/Light theme support
- 📡 Real-time WebSocket updates

## 🔗 API Endpoints

The backend runs a REST API at `http://localhost:8765`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/settings` | GET/PUT | All settings |
| `/api/settings/camera` | GET/PUT | Camera settings |
| `/api/settings/tracking` | GET/PUT | Tracking settings |
| `/api/settings/gestures` | GET/PUT | Gesture settings |
| `/api/settings/cursor` | GET/PUT | Cursor settings |
| `/api/settings/actions` | GET/PUT | Action settings |
| `/api/bindings` | GET/PUT | Gesture keybinds |
| `/api/cameras` | GET | List cameras |
| `/api/status` | GET | App status |
| `/api/control/start` | POST | Start tracking |
| `/api/control/stop` | POST | Stop tracking |
| `/api/control/toggle` | POST | Toggle pause |
| `/ws` | WebSocket | Real-time updates |

**API Documentation:** http://localhost:8765/docs

## ⚙️ Configuration

### settings.json
Located in `spatial-touch-windows/config/settings.json`:
- Camera resolution and FPS
- Tracking confidence thresholds
- Gesture detection parameters
- Cursor sensitivity and smoothing
- Action dispatcher settings

### gestures.json
Located in `spatial-touch-windows/config/gestures.json`:
- Custom gesture-to-action mappings
- Keyboard shortcuts
- Mouse actions

## 🤲 Default Gestures

| Gesture | Action |
|---------|--------|
| Pinch (thumb + index) | Left click |
| Pinch hold | Drag |
| Double pinch | Double click |
| Swipe up | Alt+Tab |
| Swipe down | Win+D (Show desktop) |

## 📝 License

MIT License - See [LICENSE](spatial-touch-windows/LICENSE)

## 🤝 Contributing

See [CONTRIBUTING.md](spatial-touch-windows/CONTRIBUTING.md) for guidelines.
