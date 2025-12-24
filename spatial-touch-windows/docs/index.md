# Spatial Touch Documentation

Welcome to the Spatial Touch documentation!

## Quick Links

- [Getting Started](getting-started.md)
- [Configuration Guide](configuration.md)
- [Gesture Reference](gestures.md)
- [API Reference](api/index.md)
- [Contributing](../CONTRIBUTING.md)

## What is Spatial Touch?

Spatial Touch is a Windows application that transforms your laptop's webcam into a touchless input device. Using advanced computer vision and hand tracking powered by MediaPipe, you can control your computer through natural mid-air gestures.

## Features

- **Cursor Control**: Move the cursor by pointing with your index finger
- **Click Actions**: Left and right click using pinch gestures
- **Drag & Drop**: Hold a pinch to drag items
- **Configurable**: Customize gestures and sensitivity via JSON config
- **Privacy First**: 100% local processing, no cloud connectivity

## Requirements

- Windows 10/11 (64-bit)
- Python 3.11+
- Webcam (720p or better recommended)
- 4GB RAM minimum

## Installation

```powershell
# Clone the repository
git clone https://github.com/spatial-touch/spatial-touch-windows.git
cd spatial-touch-windows

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run Spatial Touch
python -m spatial_touch
```

## Documentation Structure

```
docs/
├── index.md                 # This file
├── getting-started.md       # Installation and first run
├── configuration.md         # Configuration options
├── gestures.md              # Gesture reference
├── troubleshooting.md       # Common issues
├── api/                     # API documentation
│   ├── index.md
│   ├── camera.md
│   ├── hand_tracker.md
│   ├── gesture_engine.md
│   └── action_dispatcher.md
└── assets/                  # Images and resources
    ├── demo.gif
    └── icon.ico
```

## Support

- **Issues**: [GitHub Issues](https://github.com/spatial-touch/spatial-touch-windows/issues)
- **Discussions**: [GitHub Discussions](https://github.com/spatial-touch/spatial-touch-windows/discussions)
- **Discord**: [Join our server](https://discord.gg/spatialtouch)
