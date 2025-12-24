# Getting Started with Spatial Touch

This guide will help you get Spatial Touch up and running on your Windows system.

## Prerequisites

Before installing Spatial Touch, ensure you have:

- **Windows 10/11** (64-bit)
- **Python 3.11** or higher ([Download](https://www.python.org/downloads/))
- **Webcam** (built-in or USB, 720p minimum)
- **Git** (optional, for cloning) ([Download](https://git-scm.com/downloads))

## Installation

### Option 1: From Source (Recommended for Development)

```powershell
# Clone the repository
git clone https://github.com/spatial-touch/spatial-touch-windows.git
cd spatial-touch-windows

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Download Release (Coming Soon)

Pre-built executables will be available in the [Releases](https://github.com/spatial-touch/spatial-touch-windows/releases) section.

## First Run

### Starting Spatial Touch

```powershell
# Make sure you're in the project directory with venv activated
python -m spatial_touch
```

You should see:
```
Spatial Touch v0.1.0
Press Ctrl+C to exit
```

### Testing Your Setup

1. **Position yourself** about 50cm (20 inches) from your webcam
2. **Ensure good lighting** on your hands
3. **Raise your hand** in view of the camera
4. **Point with your index finger** - the cursor should move!
5. **Pinch thumb and index finger** to click

### Debug Mode

To see visual feedback and additional logging:

```powershell
python -m spatial_touch --debug
```

This opens a window showing:
- Camera feed
- Detected hand landmarks
- Current gesture state

## Configuration

Edit `config/settings.json` to customize behavior:

```json
{
  "cursor": {
    "sensitivity": 1.0,      // Increase for faster cursor
    "smoothing_factor": 0.4  // Lower for smoother movement
  },
  "gestures": {
    "pinch_threshold": 0.05  // Lower = easier to trigger
  }
}
```

See [Configuration Guide](configuration.md) for all options.

## Troubleshooting

### Camera Not Detected

```powershell
# Check available cameras
python -c "import cv2; print([cv2.VideoCapture(i).isOpened() for i in range(3)])"
```

If your camera is at a different index:
```powershell
python -m spatial_touch --camera 1
```

### Hand Not Detected

- Ensure good lighting (avoid backlight)
- Keep your hand within the camera frame
- Avoid complex backgrounds
- Try adjusting detection confidence in settings

### Cursor Jittery

Increase smoothing in `config/settings.json`:
```json
{
  "tracking": {
    "smoothing_factor": 0.3  // Lower = smoother
  }
}
```

### High CPU Usage

Enable idle optimization in settings:
```json
{
  "system": {
    "idle_fps": 5,
    "active_fps": 30
  }
}
```

## Next Steps

- [Learn all gestures](gestures.md)
- [Customize configuration](configuration.md)
- [Build standalone executable](building.md)
- [Contribute to development](../CONTRIBUTING.md)
