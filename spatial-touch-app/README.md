# Spatial Touch App

A modern Flutter application for controlling Spatial Touch hand gesture settings.

## Features

- 🎛️ **Complete Settings Control** - Adjust all sensitivity and tracking parameters
- 📷 **Camera Selection** - Switch between available webcams
- ⌨️ **Custom Keybinds** - Configure gestures to trigger any action
- 📊 **Real-time Status** - Monitor tracking status and performance
- 🌙 **Dark/Light Mode** - Beautiful UI with theme support
- 🔄 **Live Updates** - WebSocket connection for real-time sync

## Getting Started

1. Ensure Flutter 3.6+ is installed
2. Run `flutter pub get`
3. Run `flutter run -d windows`

## Connection

The app connects to the Spatial Touch Python backend via REST API on `localhost:8765`.

Start the Python backend with API enabled:
```bash
python -m spatial_touch --api
```
