# Gesture Reference

This document describes all gestures supported by Spatial Touch.

## Hand Position

For best results:
- Keep your hand **50-80cm** from the webcam
- Ensure your **entire hand** is visible
- Use a **well-lit** environment
- Avoid **cluttered backgrounds**

## Hand Landmark Reference

Spatial Touch uses MediaPipe's 21-point hand landmark model:

```
        [4] THUMB_TIP
       /
      [3] THUMB_IP
     /
    [2] THUMB_MCP ─ [1] THUMB_CMC ─ [0] WRIST
                                      │
                   [5] INDEX_MCP ─────┼───── [6] INDEX_PIP ─ [7] INDEX_DIP ─ [8] INDEX_TIP
                                      │
                   [9] MIDDLE_MCP ────┼───── [10] MIDDLE_PIP ─ [11] MIDDLE_DIP ─ [12] MIDDLE_TIP
                                      │
                   [13] RING_MCP ─────┼───── [14] RING_PIP ─ [15] RING_DIP ─ [16] RING_TIP
                                      │
                   [17] PINKY_MCP ────┴───── [18] PINKY_PIP ─ [19] PINKY_DIP ─ [20] PINKY_TIP
```

## Core Gestures

### 1. Cursor Movement

**How**: Point with your index finger

**Landmarks Used**: Index finger tip (landmark 8)

**Description**: The position of your index fingertip controls the cursor position. Movement is mapped from camera coordinates to screen coordinates.

**Tips**:
- Keep other fingers curled for cleaner detection
- Move your whole arm for large movements
- Move just your finger for precision

---

### 2. Left Click

**How**: Pinch thumb and index finger together

**Landmarks Used**: Thumb tip (4) + Index tip (8)

**Trigger**: When distance between thumb and index tips falls below threshold (~5%)

**Description**: Quickly pinch and release to perform a left click. The click is registered when you release the pinch.

**Tips**:
- Make a quick, deliberate pinch
- Avoid holding the pinch (that triggers drag)
- Wait for the debounce period between clicks

---

### 3. Right Click

**How**: Pinch thumb and middle finger together

**Landmarks Used**: Thumb tip (4) + Middle tip (12)

**Trigger**: When distance between thumb and middle tips falls below threshold

**Description**: Similar to left click, but using middle finger instead of index. Useful for context menus.

**Tips**:
- Keep index finger pointed to maintain cursor position
- Quick pinch and release

---

### 4. Drag and Drop

**How**: Pinch thumb and index finger, hold, move, release

**Landmarks Used**: Thumb tip (4) + Index tip (8)

**Trigger**: Hold pinch for 300ms (configurable)

**States**:
1. **Drag Start**: Pinch detected and held for hold_time_ms
2. **Drag Move**: Continue moving with pinch held
3. **Drag End**: Release the pinch

**Tips**:
- Wait for the hold threshold before moving
- Keep pinch tight while dragging
- Release cleanly to drop

---

## Gesture Timing

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pinch_threshold` | 0.05 | Distance threshold (normalized) |
| `debounce_ms` | 200 | Minimum time between clicks |
| `hold_time_ms` | 300 | Time before drag activates |

---

## Planned Gestures (Future)

### Scroll
- **Two-finger vertical movement** for scrolling
- Direction: up/down

### Swipe Left/Right
- **Quick horizontal swipe** for navigation
- Actions: Back, Forward

### Pinch to Zoom
- **Two-hand pinch** for zooming
- In/out based on distance change

### Open Palm
- **Show open palm** to pause/resume
- Useful for presentations

---

## Customization

Edit `config/gestures.json` to customize gesture behavior:

```json
{
  "gestures": [
    {
      "id": "left_click",
      "trigger": {
        "type": "pinch",
        "fingers": ["thumb_tip", "index_tip"],
        "threshold": 0.05
      },
      "timing": {
        "debounce_ms": 200
      }
    }
  ]
}
```

See [Configuration Guide](configuration.md) for full details.

---

## Troubleshooting Gestures

### Click not registering
- Make your pinch more deliberate
- Ensure fingers are clearly visible
- Try lowering `pinch_threshold` in config

### Accidental clicks
- Increase `debounce_ms` value
- Increase `pinch_threshold` slightly

### Drag starts too easily
- Increase `hold_time_ms` value

### Drag doesn't start
- Hold pinch longer
- Decrease `hold_time_ms` if needed
