# 📋 Spatial Touch - Project Specification

<div align="center">

**Version:** 1.0.0-alpha  
**Status:** Active Development  
**License:** MIT  
**Platform:** Windows 10/11  

</div>

---

## 📖 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Solution Overview](#solution-overview)
4. [Technical Architecture](#technical-architecture)
5. [Feature Specifications](#feature-specifications)
6. [Gesture Definitions](#gesture-definitions)
7. [Performance Requirements](#performance-requirements)
8. [Security & Privacy](#security--privacy)
9. [Development Roadmap](#development-roadmap)
10. [Success Metrics](#success-metrics)

---

## 🎯 Executive Summary

**Spatial Touch** is an open-source Windows application that transforms any laptop webcam into a touchless input device. Using advanced computer vision and hand tracking, users can control their computer through natural mid-air gestures—moving the cursor, clicking, scrolling, and performing system actions without touching any physical device.

### Key Value Propositions

| For Users | For Developers |
|-----------|----------------|
| Hands-free computer control | Clean, modular architecture |
| Accessibility enhancement | Extensive documentation |
| No additional hardware needed | Easy contribution workflow |
| Privacy-first (local processing) | Well-defined extension points |
| Low resource footprint | Comprehensive test coverage |

---

## 🔍 Problem Statement

### Current Challenges

1. **Accessibility Barriers**
   - Users with motor impairments struggle with traditional input devices
   - Existing solutions require expensive specialized hardware
   - Voice control has privacy and accuracy limitations

2. **Hygiene Concerns**
   - Shared workstations require touching common surfaces
   - Healthcare and food service environments need touchless interfaces
   - Post-pandemic awareness of contact transmission

3. **Ergonomic Issues**
   - Repetitive strain injuries from mouse/keyboard use
   - Limited input options for standing desk users
   - No intuitive way to interact during presentations

### Market Gap

Existing solutions are either:
- **Too expensive** (Leap Motion, specialized cameras)
- **Too complex** (require technical setup)
- **Too limited** (single gesture or application-specific)
- **Privacy concerning** (cloud-based processing)

---

## 💡 Solution Overview

### Core Concept

Spatial Touch creates a **virtual interaction zone** in front of the user's webcam. Hand movements within this zone are translated to mouse movements, and specific gestures trigger clicks and other actions.

```
┌─────────────────────────────────────────────────────────┐
│                    INTERACTION ZONE                      │
│                                                          │
│    ╔═══════════════════════════════════════════════╗    │
│    ║                                               ║    │
│    ║     👆 Index finger = Cursor position         ║    │
│    ║                                               ║    │
│    ║     🤏 Thumb + Index = Left click             ║    │
│    ║                                               ║    │
│    ║     🤏 Thumb + Middle = Right click           ║    │
│    ║                                               ║    │
│    ╚═══════════════════════════════════════════════╝    │
│                                                          │
│                      📷 WEBCAM                           │
└─────────────────────────────────────────────────────────┘
```

### Design Philosophy

1. **Invisible by Default** — Runs silently in background
2. **Privacy First** — Zero data leaves the device
3. **Performance Focused** — Minimal CPU/memory footprint
4. **Accessibility Centered** — Works for diverse users
5. **Developer Friendly** — Easy to extend and customize

---

## 🏗️ Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SPATIAL TOUCH                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Camera     │───▶│    Hand      │───▶│   Gesture    │       │
│  │   Manager    │    │   Tracker    │    │   Engine     │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│         │                    │                   │               │
│         │                    │                   ▼               │
│         │                    │           ┌──────────────┐       │
│         │                    │           │    Action    │       │
│         │                    │           │  Dispatcher  │       │
│         │                    │           └──────┬───────┘       │
│         │                    │                   │               │
│         ▼                    ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CONFIGURATION                         │   │
│  │              (settings.json, gestures.json)             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                        SYSTEM LAYER                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │  Windows   │  │   System   │  │   Task     │                │
│  │  SendInput │  │   Tray     │  │  Scheduler │                │
│  └────────────┘  └────────────┘  └────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **Camera Manager** | Capture frames from webcam | Device index | RGB frames |
| **Hand Tracker** | Detect hand landmarks | RGB frame | 21 landmarks + confidence |
| **Gesture Engine** | Recognize gestures from landmarks | Landmarks | Gesture events |
| **Zone Mapper** | Map coordinates to screen regions | Hand position | Screen coordinates |
| **Action Dispatcher** | Execute OS-level actions | Gesture events | Mouse/KB events |
| **Config Manager** | Load and manage settings | JSON files | Configuration objects |

### Data Flow

```
Camera Frame (30 FPS)
        │
        ▼
   ┌─────────┐
   │ Resize  │ 640x480 (processing)
   └────┬────┘
        │
        ▼
   ┌─────────────────┐
   │ MediaPipe Hands │ Hand detection + tracking
   └────────┬────────┘
            │
            ▼
   ┌────────────────────┐
   │ Landmark Smoother  │ Exponential moving average
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Gesture Detector  │ Distance + velocity + state
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Action Executor   │ pyautogui / pynput
   └────────────────────┘
```

### Technology Choices

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Language** | Python 3.11+ | Rapid development, excellent CV libraries |
| **Camera** | OpenCV 4.x | Industry standard, cross-platform |
| **Hand Tracking** | MediaPipe | Best accuracy/performance balance, free |
| **OS Input** | pyautogui + pynput | Reliable Windows input injection |
| **Configuration** | JSON + Pydantic | Human-readable, validated at load |
| **Logging** | Python logging + structlog | Structured, rotatable logs |
| **Packaging** | PyInstaller | Single executable distribution |
| **Testing** | pytest | Industry standard, great fixtures |

---

## 🎮 Feature Specifications

### Phase 1: Core MVP (v0.1.0)

#### F1.1: Cursor Control
| Spec | Value |
|------|-------|
| Input | Index finger tip position |
| Mapping | Camera coords → Screen coords |
| Smoothing | EMA with α = 0.4 |
| Sensitivity | Configurable (0.5x - 2.0x) |
| Dead Zone | 2% of frame (configurable) |

#### F1.2: Left Click
| Spec | Value |
|------|-------|
| Trigger | Thumb-to-index distance < 5% |
| Debounce | 200ms minimum between clicks |
| Feedback | Optional click sound |

#### F1.3: Right Click
| Spec | Value |
|------|-------|
| Trigger | Thumb-to-middle distance < 5% |
| Debounce | 200ms minimum between clicks |

#### F1.4: Drag and Drop
| Spec | Value |
|------|-------|
| Trigger | Pinch hold > 300ms |
| Release | Pinch open |
| Movement | Cursor follows index finger |

### Phase 2: Enhanced (v0.2.0)

#### F2.1: Scroll Gesture
- **Trigger:** Two fingers visible + vertical movement
- **Sensitivity:** Configurable scroll speed
- **Direction:** Natural or inverted (configurable)

#### F2.2: System Tray Integration
- Tray icon with status indicator
- Quick settings menu
- Enable/disable toggle
- Exit option

#### F2.3: Keyboard Shortcuts
- `Ctrl+Alt+S`: Toggle Spatial Touch
- `Ctrl+Alt+P`: Pause/Resume
- Configurable shortcuts

### Phase 3: Advanced (v0.3.0)

#### F3.1: Zone-Based Actions
```
┌──────────┬──────────┬──────────┐
│   TOP    │   TOP    │   TOP    │
│   LEFT   │  CENTER  │  RIGHT   │
├──────────┼──────────┼──────────┤
│  MIDDLE  │  MIDDLE  │  MIDDLE  │
│   LEFT   │  CENTER  │  RIGHT   │
├──────────┼──────────┼──────────┤
│  BOTTOM  │  BOTTOM  │  BOTTOM  │
│   LEFT   │  CENTER  │  RIGHT   │
└──────────┴──────────┴──────────┘
```

Each zone can trigger different actions based on entry/exit.

#### F3.2: Swipe Gestures
| Gesture | Default Action |
|---------|---------------|
| Swipe Left | Back (Alt+Left) |
| Swipe Right | Forward (Alt+Right) |
| Swipe Up | Task View |
| Swipe Down | Minimize |

#### F3.3: Per-Application Profiles
- Different gesture mappings per application
- Auto-detection of active window
- Profile switching

### Phase 4: Polish (v1.0.0)

- Installer with Windows integration
- Onboarding wizard
- Gesture tutorial
- Calibration tool
- Usage statistics (local only)
- Automatic updates

---

## ✋ Gesture Definitions

### Hand Landmark Reference

```
        [4] Thumb Tip
       /
      [3]
     /
    [2]──[1]──[0] Wrist
              │
         [5]──┼──[6]──[7]──[8] Index Tip
              │
         [9]──┼──[10]─[11]─[12] Middle Tip
              │
         [13]─┼──[14]─[15]─[16] Ring Tip
              │
         [17]─┴──[18]─[19]─[20] Pinky Tip
```

### Gesture Detection Algorithms

#### Pinch Detection
```python
def is_pinch(thumb_tip, finger_tip, threshold=0.05):
    distance = euclidean_distance(thumb_tip, finger_tip)
    return distance < threshold
```

#### Gesture State Machine
```
    ┌──────────────────────────────────────────┐
    │                                          │
    ▼                                          │
┌───────┐    pinch detected    ┌───────────┐   │
│ IDLE  │─────────────────────▶│ TRIGGERED │   │
└───────┘                      └─────┬─────┘   │
    ▲                                │         │
    │                         hold > 300ms     │
    │                                │         │
    │                                ▼         │
    │                          ┌─────────┐     │
    │ pinch released           │ HOLDING │     │
    └──────────────────────────┴─────────┘     │
                                     │         │
                              pinch released   │
                                     │         │
                                     └─────────┘
```

### Gesture Configuration Schema

```json
{
  "gesture_id": "thumb_index_pinch",
  "detection": {
    "landmarks": [4, 8],
    "method": "distance",
    "threshold": 0.05,
    "threshold_unit": "normalized"
  },
  "timing": {
    "debounce_ms": 200,
    "hold_threshold_ms": 300,
    "max_velocity": 0.1
  },
  "action": {
    "on_trigger": "mouse_left_down",
    "on_release": "mouse_left_up",
    "on_hold": "mouse_drag"
  }
}
```

---

## ⚡ Performance Requirements

### Latency Budget

```
┌─────────────────────────────────────────────────────────────┐
│                    TOTAL: < 50ms                             │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Capture    │   Tracking   │   Gesture    │    Action     │
│   < 10ms     │   < 25ms     │   < 10ms     │    < 5ms      │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

### Resource Limits

| State | CPU | Memory | GPU |
|-------|-----|--------|-----|
| **Idle** (no hand) | < 2% | < 100MB | 0% |
| **Active** (tracking) | < 10% | < 200MB | < 5% |
| **Peak** (gesture) | < 15% | < 250MB | < 10% |

### Optimization Strategies

1. **Adaptive Frame Rate**
   - Reduce FPS when no hand detected
   - Increase FPS during active interaction

2. **Region of Interest**
   - Track hand position and crop frame
   - Smaller processing area = faster inference

3. **Model Selection**
   - Use MediaPipe's "lite" model by default
   - Option for "full" model on powerful hardware

4. **Threading**
   - Capture in background thread
   - Processing in main thread
   - Non-blocking action dispatch

---

## 🔒 Security & Privacy

### Privacy Principles

1. **Zero Cloud** — All processing happens locally
2. **Zero Storage** — No frames saved to disk
3. **Zero Transmission** — No network activity
4. **User Control** — Camera only active when enabled

### Data Handling

| Data Type | Storage | Retention | Transmission |
|-----------|---------|-----------|--------------|
| Camera frames | RAM only | Immediate discard | Never |
| Landmarks | RAM only | Current frame only | Never |
| Configuration | Local disk | Persistent | Never |
| Logs | Local disk | 7 days rolling | Never |

### Security Measures

- No elevated privileges required
- No system file modifications
- Signed executable (future)
- Code scanning in CI/CD

### Transparency

- Open source code
- Clear privacy policy
- Visible camera indicator (Windows native)
- Easy enable/disable

---

## 🗓️ Development Roadmap

### Timeline Overview

```
2024 Q1 ──────────────────────────────────────────────────────────▶
         │                                                         │
     [v0.1.0]                                                  [v1.0.0]
      MVP                                                      Stable
         │                                                         │
         ▼                                                         ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌─────────┐
│  Core Engine   │  │   Gestures     │  │    Polish      │  │ Release │
│  - Camera      │  │   - Scroll     │  │    - Tray      │  │ - Docs  │
│  - Tracking    │  │   - Swipes     │  │    - Installer │  │ - Site  │
│  - Click       │  │   - Zones      │  │    - Tutorial  │  │ - Video │
└────────────────┘  └────────────────┘  └────────────────┘  └─────────┘
     Week 1-2            Week 3-4            Week 5-6         Week 7-8
```

### Milestone Details

#### v0.1.0 - Core MVP
- [ ] Camera capture module
- [ ] Hand tracking integration
- [ ] Basic cursor movement
- [ ] Left/right click
- [ ] Configuration loading
- [ ] Logging infrastructure

#### v0.2.0 - Enhanced Gestures
- [ ] Drag and drop
- [ ] Scroll gesture
- [ ] System tray
- [ ] Keyboard shortcuts
- [ ] Performance optimization

#### v0.3.0 - Advanced Features
- [ ] Zone-based actions
- [ ] Swipe gestures
- [ ] Per-app profiles
- [ ] Calibration tool

#### v1.0.0 - Production Release
- [ ] Windows installer
- [ ] Auto-update mechanism
- [ ] Onboarding wizard
- [ ] Full documentation
- [ ] Website and demo

---

## 📊 Success Metrics

### Technical KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| End-to-end latency | < 50ms | Timestamp delta |
| Click accuracy | > 95% | User testing |
| False positive rate | < 5% | Gesture logging |
| CPU usage | < 10% | System monitor |
| Crash rate | < 0.1% | Error logging |

### User Adoption KPIs

| Metric | Target | Source |
|--------|--------|--------|
| GitHub stars | 1,000+ (Y1) | GitHub |
| Daily active users | 500+ (Y1) | Opt-in analytics |
| User retention (30d) | > 40% | Opt-in analytics |
| Issue resolution time | < 48h | GitHub issues |

### Quality Metrics

| Metric | Target | Tool |
|--------|--------|------|
| Code coverage | > 80% | pytest-cov |
| Documentation coverage | 100% public API | interrogate |
| Lint score | 10/10 | pylint |
| Type coverage | > 90% | mypy |

---

## 📚 Appendices

### A. Glossary

| Term | Definition |
|------|------------|
| **Landmark** | A point on the hand detected by MediaPipe (21 total) |
| **Pinch** | Touching thumb to another fingertip |
| **Debounce** | Delay to prevent rapid repeated triggers |
| **Dead Zone** | Area where movement is ignored |
| **EMA** | Exponential Moving Average (smoothing) |

### B. References

- [MediaPipe Hands Documentation](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [Windows Input API](https://docs.microsoft.com/en-us/windows/win32/inputdev/user-input)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)

### C. Related Projects

- Leap Motion (hardware-based)
- OpenTrack (head tracking)
- GestIC (Microchip)
- Ultraleap (commercial)

---

<div align="center">

**Built with ❤️ for accessibility**

[GitHub](https://github.com/spatial-touch) · [Documentation](https://spatial-touch.dev) · [Discord](https://discord.gg/spatial-touch)

</div>
