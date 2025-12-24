import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/settings_models.dart';
import '../../../core/services/api_service.dart';

/// All settings provider with async loading
final settingsProvider = AsyncNotifierProvider<SettingsNotifier, AllSettings>(() {
  return SettingsNotifier();
});

/// Connection status provider
final connectionStatusProvider = StateProvider<bool>((ref) => false);

/// App status provider
final appStatusProvider = StateNotifierProvider<AppStatusNotifier, AppStatus>((ref) {
  return AppStatusNotifier(ref);
});

/// Camera list provider
final camerasProvider = FutureProvider<List<CameraInfo>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.listCameras();
});

/// Gesture bindings provider
final bindingsProvider = AsyncNotifierProvider<BindingsNotifier, List<GestureBinding>>(() {
  return BindingsNotifier();
});


class SettingsNotifier extends AsyncNotifier<AllSettings> {
  @override
  Future<AllSettings> build() async {
    return await _loadSettings();
  }
  
  Future<AllSettings> _loadSettings() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final isConnected = await apiService.testConnection();
      ref.read(connectionStatusProvider.notifier).state = isConnected;
      
      if (isConnected) {
        return await apiService.getSettings();
      } else {
        return AllSettings(); // Default settings
      }
    } catch (e) {
      ref.read(connectionStatusProvider.notifier).state = false;
      return AllSettings(); // Default settings on error
    }
  }
  
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _loadSettings());
  }
  
  Future<void> updateSettings(AllSettings settings) async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final updated = await apiService.updateSettings(settings);
      state = AsyncValue.data(updated);
    } catch (e) {
      // Revert on error
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
  
  Future<void> updateCamera(CameraSettings camera) async {
    final current = state.valueOrNull ?? AllSettings();
    await updateSettings(current.copyWith(camera: camera));
  }
  
  Future<void> updateTracking(TrackingSettings tracking) async {
    final current = state.valueOrNull ?? AllSettings();
    await updateSettings(current.copyWith(tracking: tracking));
  }
  
  Future<void> updateGestures(GestureSettings gestures) async {
    final current = state.valueOrNull ?? AllSettings();
    await updateSettings(current.copyWith(gestures: gestures));
  }
  
  Future<void> updateCursor(CursorSettings cursor) async {
    final current = state.valueOrNull ?? AllSettings();
    await updateSettings(current.copyWith(cursor: cursor));
  }
  
  Future<void> updateActions(ActionSettings actions) async {
    final current = state.valueOrNull ?? AllSettings();
    await updateSettings(current.copyWith(actions: actions));
  }
  
  Future<void> updateSystem(SystemSettings system) async {
    final current = state.valueOrNull ?? AllSettings();
    await updateSettings(current.copyWith(system: system));
  }
}


class AppStatusNotifier extends StateNotifier<AppStatus> {
  final Ref ref;
  Timer? _pollingTimer;
  
  AppStatusNotifier(this.ref) : super(AppStatus()) {
    _startPolling();
  }
  
  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 2), (_) async {
      await refreshStatus();
    });
  }
  
  Future<void> refreshStatus() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final status = await apiService.getStatus();
      state = status;
    } catch (e) {
      // Connection lost
      state = AppStatus();
    }
  }
  
  Future<void> start() async {
    final apiService = ref.read(apiServiceProvider);
    await apiService.startTracking();
    await refreshStatus();
  }
  
  Future<void> stop() async {
    final apiService = ref.read(apiServiceProvider);
    await apiService.stopTracking();
    await refreshStatus();
  }
  
  Future<void> pause() async {
    final apiService = ref.read(apiServiceProvider);
    await apiService.pauseTracking();
    await refreshStatus();
  }
  
  Future<void> resume() async {
    final apiService = ref.read(apiServiceProvider);
    await apiService.resumeTracking();
    await refreshStatus();
  }
  
  Future<void> toggle() async {
    final apiService = ref.read(apiServiceProvider);
    await apiService.toggleTracking();
    await refreshStatus();
  }
  
  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }
}


class BindingsNotifier extends AsyncNotifier<List<GestureBinding>> {
  @override
  Future<List<GestureBinding>> build() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      return await apiService.getBindings();
    } catch (e) {
      return _defaultBindings();
    }
  }
  
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final apiService = ref.read(apiServiceProvider);
      return await apiService.getBindings();
    });
  }
  
  Future<void> updateBindings(List<GestureBinding> bindings) async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final updated = await apiService.updateBindings(bindings);
      state = AsyncValue.data(updated);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
  
  Future<void> addBinding(GestureBinding binding) async {
    final current = state.valueOrNull ?? [];
    await updateBindings([...current, binding]);
  }
  
  Future<void> removeBinding(String gesture) async {
    final current = state.valueOrNull ?? [];
    await updateBindings(current.where((b) => b.gesture != gesture).toList());
  }
  
  Future<void> toggleBinding(String gesture, bool enabled) async {
    final current = state.valueOrNull ?? [];
    final updated = current.map((b) {
      if (b.gesture == gesture) {
        return b.copyWith(enabled: enabled);
      }
      return b;
    }).toList();
    await updateBindings(updated);
  }
  
  List<GestureBinding> _defaultBindings() {
    return [
      GestureBinding(gesture: 'pinch', action: 'mouse', value: 'left_click'),
      GestureBinding(gesture: 'pinch_hold', action: 'mouse', value: 'left_down'),
      GestureBinding(gesture: 'pinch_release', action: 'mouse', value: 'left_up'),
      GestureBinding(gesture: 'double_tap', action: 'mouse', value: 'double_click'),
      GestureBinding(gesture: 'swipe_up', action: 'key', value: 'ctrl+alt+tab'),
      GestureBinding(gesture: 'swipe_down', action: 'key', value: 'win+d'),
    ];
  }
}
