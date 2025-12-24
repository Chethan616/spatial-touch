/// Settings data models for Spatial Touch

// ============================================================================
// Camera Settings
// ============================================================================

class CameraSettings {
  final int deviceIndex;
  final List<int> resolution;
  final int fps;
  final bool autoReconnect;
  final double reconnectDelay;
  final int warmupFrames;
  
  CameraSettings({
    this.deviceIndex = 0,
    this.resolution = const [1280, 720],
    this.fps = 30,
    this.autoReconnect = true,
    this.reconnectDelay = 2.0,
    this.warmupFrames = 10,
  });
  
  factory CameraSettings.fromJson(Map<String, dynamic> json) {
    return CameraSettings(
      deviceIndex: json['device_index'] ?? 0,
      resolution: List<int>.from(json['resolution'] ?? [1280, 720]),
      fps: json['fps'] ?? 30,
      autoReconnect: json['auto_reconnect'] ?? true,
      reconnectDelay: (json['reconnect_delay'] ?? 2.0).toDouble(),
      warmupFrames: json['warmup_frames'] ?? 10,
    );
  }
  
  Map<String, dynamic> toJson() => {
    'device_index': deviceIndex,
    'resolution': resolution,
    'fps': fps,
    'auto_reconnect': autoReconnect,
    'reconnect_delay': reconnectDelay,
    'warmup_frames': warmupFrames,
  };
  
  CameraSettings copyWith({
    int? deviceIndex,
    List<int>? resolution,
    int? fps,
    bool? autoReconnect,
    double? reconnectDelay,
    int? warmupFrames,
  }) {
    return CameraSettings(
      deviceIndex: deviceIndex ?? this.deviceIndex,
      resolution: resolution ?? this.resolution,
      fps: fps ?? this.fps,
      autoReconnect: autoReconnect ?? this.autoReconnect,
      reconnectDelay: reconnectDelay ?? this.reconnectDelay,
      warmupFrames: warmupFrames ?? this.warmupFrames,
    );
  }
}

// ============================================================================
// Tracking Settings
// ============================================================================

class TrackingSettings {
  final int maxHands;
  final double minDetectionConfidence;
  final double minTrackingConfidence;
  final int modelComplexity;
  final double smoothingFactor;
  
  TrackingSettings({
    this.maxHands = 1,
    this.minDetectionConfidence = 0.7,
    this.minTrackingConfidence = 0.5,
    this.modelComplexity = 1,
    this.smoothingFactor = 0.4,
  });
  
  factory TrackingSettings.fromJson(Map<String, dynamic> json) {
    return TrackingSettings(
      maxHands: json['max_hands'] ?? 1,
      minDetectionConfidence: (json['min_detection_confidence'] ?? 0.7).toDouble(),
      minTrackingConfidence: (json['min_tracking_confidence'] ?? 0.5).toDouble(),
      modelComplexity: json['model_complexity'] ?? 1,
      smoothingFactor: (json['smoothing_factor'] ?? 0.4).toDouble(),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'max_hands': maxHands,
    'min_detection_confidence': minDetectionConfidence,
    'min_tracking_confidence': minTrackingConfidence,
    'model_complexity': modelComplexity,
    'smoothing_factor': smoothingFactor,
  };
  
  TrackingSettings copyWith({
    int? maxHands,
    double? minDetectionConfidence,
    double? minTrackingConfidence,
    int? modelComplexity,
    double? smoothingFactor,
  }) {
    return TrackingSettings(
      maxHands: maxHands ?? this.maxHands,
      minDetectionConfidence: minDetectionConfidence ?? this.minDetectionConfidence,
      minTrackingConfidence: minTrackingConfidence ?? this.minTrackingConfidence,
      modelComplexity: modelComplexity ?? this.modelComplexity,
      smoothingFactor: smoothingFactor ?? this.smoothingFactor,
    );
  }
}

// ============================================================================
// Gesture Settings
// ============================================================================

class GestureSettings {
  final double pinchThreshold;
  final int debounceMs;
  final int holdTimeMs;
  final int clickReleaseMs;
  final double velocityThreshold;
  
  GestureSettings({
    this.pinchThreshold = 0.05,
    this.debounceMs = 200,
    this.holdTimeMs = 300,
    this.clickReleaseMs = 200,
    this.velocityThreshold = 0.01,
  });
  
  factory GestureSettings.fromJson(Map<String, dynamic> json) {
    return GestureSettings(
      pinchThreshold: (json['pinch_threshold'] ?? 0.05).toDouble(),
      debounceMs: json['debounce_ms'] ?? 200,
      holdTimeMs: json['hold_time_ms'] ?? 300,
      clickReleaseMs: json['click_release_ms'] ?? 200,
      velocityThreshold: (json['velocity_threshold'] ?? 0.01).toDouble(),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'pinch_threshold': pinchThreshold,
    'debounce_ms': debounceMs,
    'hold_time_ms': holdTimeMs,
    'click_release_ms': clickReleaseMs,
    'velocity_threshold': velocityThreshold,
  };
  
  GestureSettings copyWith({
    double? pinchThreshold,
    int? debounceMs,
    int? holdTimeMs,
    int? clickReleaseMs,
    double? velocityThreshold,
  }) {
    return GestureSettings(
      pinchThreshold: pinchThreshold ?? this.pinchThreshold,
      debounceMs: debounceMs ?? this.debounceMs,
      holdTimeMs: holdTimeMs ?? this.holdTimeMs,
      clickReleaseMs: clickReleaseMs ?? this.clickReleaseMs,
      velocityThreshold: velocityThreshold ?? this.velocityThreshold,
    );
  }
}

// ============================================================================
// Cursor Settings
// ============================================================================

class CursorSettings {
  final double sensitivity;
  final double deadZone;
  final bool invertX;
  final bool invertY;
  final int margin;
  final double smoothing;
  
  CursorSettings({
    this.sensitivity = 1.0,
    this.deadZone = 0.02,
    this.invertX = true,
    this.invertY = false,
    this.margin = 10,
    this.smoothing = 0.0,
  });
  
  factory CursorSettings.fromJson(Map<String, dynamic> json) {
    return CursorSettings(
      sensitivity: (json['sensitivity'] ?? 1.0).toDouble(),
      deadZone: (json['dead_zone'] ?? 0.02).toDouble(),
      invertX: json['invert_x'] ?? true,
      invertY: json['invert_y'] ?? false,
      margin: json['margin'] ?? 10,
      smoothing: (json['smoothing'] ?? 0.0).toDouble(),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'sensitivity': sensitivity,
    'dead_zone': deadZone,
    'invert_x': invertX,
    'invert_y': invertY,
    'margin': margin,
    'smoothing': smoothing,
  };
  
  CursorSettings copyWith({
    double? sensitivity,
    double? deadZone,
    bool? invertX,
    bool? invertY,
    int? margin,
    double? smoothing,
  }) {
    return CursorSettings(
      sensitivity: sensitivity ?? this.sensitivity,
      deadZone: deadZone ?? this.deadZone,
      invertX: invertX ?? this.invertX,
      invertY: invertY ?? this.invertY,
      margin: margin ?? this.margin,
      smoothing: smoothing ?? this.smoothing,
    );
  }
}

// ============================================================================
// Action Settings
// ============================================================================

class ActionSettings {
  final bool enableMouse;
  final bool enableKeyboard;
  final double moveDuration;
  final double clickInterval;
  final int scrollAmount;
  final bool safeMode;
  
  ActionSettings({
    this.enableMouse = true,
    this.enableKeyboard = true,
    this.moveDuration = 0.0,
    this.clickInterval = 0.1,
    this.scrollAmount = 3,
    this.safeMode = true,
  });
  
  factory ActionSettings.fromJson(Map<String, dynamic> json) {
    return ActionSettings(
      enableMouse: json['enable_mouse'] ?? true,
      enableKeyboard: json['enable_keyboard'] ?? true,
      moveDuration: (json['move_duration'] ?? 0.0).toDouble(),
      clickInterval: (json['click_interval'] ?? 0.1).toDouble(),
      scrollAmount: json['scroll_amount'] ?? 3,
      safeMode: json['safe_mode'] ?? true,
    );
  }
  
  Map<String, dynamic> toJson() => {
    'enable_mouse': enableMouse,
    'enable_keyboard': enableKeyboard,
    'move_duration': moveDuration,
    'click_interval': clickInterval,
    'scroll_amount': scrollAmount,
    'safe_mode': safeMode,
  };
  
  ActionSettings copyWith({
    bool? enableMouse,
    bool? enableKeyboard,
    double? moveDuration,
    double? clickInterval,
    int? scrollAmount,
    bool? safeMode,
  }) {
    return ActionSettings(
      enableMouse: enableMouse ?? this.enableMouse,
      enableKeyboard: enableKeyboard ?? this.enableKeyboard,
      moveDuration: moveDuration ?? this.moveDuration,
      clickInterval: clickInterval ?? this.clickInterval,
      scrollAmount: scrollAmount ?? this.scrollAmount,
      safeMode: safeMode ?? this.safeMode,
    );
  }
}

// ============================================================================
// System Settings
// ============================================================================

class SystemSettings {
  final String logLevel;
  final bool debugMode;
  final int idleFps;
  final int activeFps;
  final bool runOnStartup;
  final bool showTrayIcon;
  
  SystemSettings({
    this.logLevel = 'INFO',
    this.debugMode = false,
    this.idleFps = 5,
    this.activeFps = 30,
    this.runOnStartup = false,
    this.showTrayIcon = true,
  });
  
  factory SystemSettings.fromJson(Map<String, dynamic> json) {
    return SystemSettings(
      logLevel: json['log_level'] ?? 'INFO',
      debugMode: json['debug_mode'] ?? false,
      idleFps: json['idle_fps'] ?? 5,
      activeFps: json['active_fps'] ?? 30,
      runOnStartup: json['run_on_startup'] ?? false,
      showTrayIcon: json['show_tray_icon'] ?? true,
    );
  }
  
  Map<String, dynamic> toJson() => {
    'log_level': logLevel,
    'debug_mode': debugMode,
    'idle_fps': idleFps,
    'active_fps': activeFps,
    'run_on_startup': runOnStartup,
    'show_tray_icon': showTrayIcon,
  };
  
  SystemSettings copyWith({
    String? logLevel,
    bool? debugMode,
    int? idleFps,
    int? activeFps,
    bool? runOnStartup,
    bool? showTrayIcon,
  }) {
    return SystemSettings(
      logLevel: logLevel ?? this.logLevel,
      debugMode: debugMode ?? this.debugMode,
      idleFps: idleFps ?? this.idleFps,
      activeFps: activeFps ?? this.activeFps,
      runOnStartup: runOnStartup ?? this.runOnStartup,
      showTrayIcon: showTrayIcon ?? this.showTrayIcon,
    );
  }
}

// ============================================================================
// All Settings
// ============================================================================

class AllSettings {
  final CameraSettings camera;
  final TrackingSettings tracking;
  final GestureSettings gestures;
  final CursorSettings cursor;
  final ActionSettings actions;
  final SystemSettings system;
  
  AllSettings({
    CameraSettings? camera,
    TrackingSettings? tracking,
    GestureSettings? gestures,
    CursorSettings? cursor,
    ActionSettings? actions,
    SystemSettings? system,
  }) :
    camera = camera ?? CameraSettings(),
    tracking = tracking ?? TrackingSettings(),
    gestures = gestures ?? GestureSettings(),
    cursor = cursor ?? CursorSettings(),
    actions = actions ?? ActionSettings(),
    system = system ?? SystemSettings();
  
  factory AllSettings.fromJson(Map<String, dynamic> json) {
    return AllSettings(
      camera: CameraSettings.fromJson(json['camera'] ?? {}),
      tracking: TrackingSettings.fromJson(json['tracking'] ?? {}),
      gestures: GestureSettings.fromJson(json['gestures'] ?? {}),
      cursor: CursorSettings.fromJson(json['cursor'] ?? {}),
      actions: ActionSettings.fromJson(json['actions'] ?? {}),
      system: SystemSettings.fromJson(json['system'] ?? {}),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'camera': camera.toJson(),
    'tracking': tracking.toJson(),
    'gestures': gestures.toJson(),
    'cursor': cursor.toJson(),
    'actions': actions.toJson(),
    'system': system.toJson(),
  };
  
  AllSettings copyWith({
    CameraSettings? camera,
    TrackingSettings? tracking,
    GestureSettings? gestures,
    CursorSettings? cursor,
    ActionSettings? actions,
    SystemSettings? system,
  }) {
    return AllSettings(
      camera: camera ?? this.camera,
      tracking: tracking ?? this.tracking,
      gestures: gestures ?? this.gestures,
      cursor: cursor ?? this.cursor,
      actions: actions ?? this.actions,
      system: system ?? this.system,
    );
  }
}

// ============================================================================
// Gesture Binding
// ============================================================================

class GestureBinding {
  final String gesture;
  final String action;
  final String value;
  final bool enabled;
  
  GestureBinding({
    required this.gesture,
    required this.action,
    required this.value,
    this.enabled = true,
  });
  
  factory GestureBinding.fromJson(Map<String, dynamic> json) {
    return GestureBinding(
      gesture: json['gesture'] ?? '',
      action: json['action'] ?? '',
      value: json['value'] ?? '',
      enabled: json['enabled'] ?? true,
    );
  }
  
  Map<String, dynamic> toJson() => {
    'gesture': gesture,
    'action': action,
    'value': value,
    'enabled': enabled,
  };
  
  GestureBinding copyWith({
    String? gesture,
    String? action,
    String? value,
    bool? enabled,
  }) {
    return GestureBinding(
      gesture: gesture ?? this.gesture,
      action: action ?? this.action,
      value: value ?? this.value,
      enabled: enabled ?? this.enabled,
    );
  }
}

// ============================================================================
// Camera Info
// ============================================================================

class CameraInfo {
  final int index;
  final String name;
  final List<List<int>> resolutions;
  final bool isCurrent;
  
  CameraInfo({
    required this.index,
    required this.name,
    required this.resolutions,
    this.isCurrent = false,
  });
  
  factory CameraInfo.fromJson(Map<String, dynamic> json) {
    return CameraInfo(
      index: json['index'] ?? 0,
      name: json['name'] ?? 'Unknown',
      resolutions: (json['resolutions'] as List?)
          ?.map((e) => List<int>.from(e))
          .toList() ?? [],
      isCurrent: json['is_current'] ?? false,
    );
  }
  
  Map<String, dynamic> toJson() => {
    'index': index,
    'name': name,
    'resolutions': resolutions,
    'is_current': isCurrent,
  };
}

// ============================================================================
// App Status
// ============================================================================

class AppStatus {
  final bool running;
  final bool paused;
  final bool trackingActive;
  final bool cameraConnected;
  final double fpsActual;
  final int frameCount;
  final int gesturesDetected;
  
  AppStatus({
    this.running = false,
    this.paused = false,
    this.trackingActive = false,
    this.cameraConnected = false,
    this.fpsActual = 0.0,
    this.frameCount = 0,
    this.gesturesDetected = 0,
  });
  
  factory AppStatus.fromJson(Map<String, dynamic> json) {
    return AppStatus(
      running: json['running'] ?? false,
      paused: json['paused'] ?? false,
      trackingActive: json['tracking_active'] ?? false,
      cameraConnected: json['camera_connected'] ?? false,
      fpsActual: (json['fps_actual'] ?? 0.0).toDouble(),
      frameCount: json['frame_count'] ?? 0,
      gesturesDetected: json['gestures_detected'] ?? 0,
    );
  }
  
  Map<String, dynamic> toJson() => {
    'running': running,
    'paused': paused,
    'tracking_active': trackingActive,
    'camera_connected': cameraConnected,
    'fps_actual': fpsActual,
    'frame_count': frameCount,
    'gestures_detected': gesturesDetected,
  };
}
