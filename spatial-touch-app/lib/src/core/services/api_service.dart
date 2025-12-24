import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/api_config.dart';
import '../../features/settings/models/settings_models.dart';

/// API Service provider
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

/// REST API service for communicating with Spatial Touch backend
class ApiService {
  late final Dio _dio;
  
  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.timeout,
      receiveTimeout: ApiConfig.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    // Add logging interceptor for debugging
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (obj) => print('[API] $obj'),
    ));
  }
  
  // ============================================================================
  // Connection
  // ============================================================================
  
  /// Test connection to the backend
  Future<bool> testConnection() async {
    try {
      final response = await _dio.get(ApiConfig.status);
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  // ============================================================================
  // Settings
  // ============================================================================
  
  /// Get all settings
  Future<AllSettings> getSettings() async {
    final response = await _dio.get(ApiConfig.settings);
    return AllSettings.fromJson(response.data);
  }
  
  /// Update all settings
  Future<AllSettings> updateSettings(AllSettings settings) async {
    final response = await _dio.put(
      ApiConfig.settings,
      data: settings.toJson(),
    );
    return AllSettings.fromJson(response.data);
  }
  
  /// Get camera settings
  Future<CameraSettings> getCameraSettings() async {
    final response = await _dio.get('${ApiConfig.settings}/camera');
    return CameraSettings.fromJson(response.data);
  }
  
  /// Update camera settings
  Future<CameraSettings> updateCameraSettings(CameraSettings settings) async {
    final response = await _dio.put(
      '${ApiConfig.settings}/camera',
      data: settings.toJson(),
    );
    return CameraSettings.fromJson(response.data);
  }
  
  /// Get tracking settings
  Future<TrackingSettings> getTrackingSettings() async {
    final response = await _dio.get('${ApiConfig.settings}/tracking');
    return TrackingSettings.fromJson(response.data);
  }
  
  /// Update tracking settings
  Future<TrackingSettings> updateTrackingSettings(TrackingSettings settings) async {
    final response = await _dio.put(
      '${ApiConfig.settings}/tracking',
      data: settings.toJson(),
    );
    return TrackingSettings.fromJson(response.data);
  }
  
  /// Get gesture settings
  Future<GestureSettings> getGestureSettings() async {
    final response = await _dio.get('${ApiConfig.settings}/gestures');
    return GestureSettings.fromJson(response.data);
  }
  
  /// Update gesture settings
  Future<GestureSettings> updateGestureSettings(GestureSettings settings) async {
    final response = await _dio.put(
      '${ApiConfig.settings}/gestures',
      data: settings.toJson(),
    );
    return GestureSettings.fromJson(response.data);
  }
  
  /// Get cursor settings
  Future<CursorSettings> getCursorSettings() async {
    final response = await _dio.get('${ApiConfig.settings}/cursor');
    return CursorSettings.fromJson(response.data);
  }
  
  /// Update cursor settings
  Future<CursorSettings> updateCursorSettings(CursorSettings settings) async {
    final response = await _dio.put(
      '${ApiConfig.settings}/cursor',
      data: settings.toJson(),
    );
    return CursorSettings.fromJson(response.data);
  }
  
  /// Get action settings
  Future<ActionSettings> getActionSettings() async {
    final response = await _dio.get('${ApiConfig.settings}/actions');
    return ActionSettings.fromJson(response.data);
  }
  
  /// Update action settings
  Future<ActionSettings> updateActionSettings(ActionSettings settings) async {
    final response = await _dio.put(
      '${ApiConfig.settings}/actions',
      data: settings.toJson(),
    );
    return ActionSettings.fromJson(response.data);
  }
  
  // ============================================================================
  // Gesture Bindings
  // ============================================================================
  
  /// Get all gesture bindings
  Future<List<GestureBinding>> getBindings() async {
    final response = await _dio.get(ApiConfig.bindings);
    return (response.data as List)
        .map((e) => GestureBinding.fromJson(e))
        .toList();
  }
  
  /// Update all gesture bindings
  Future<List<GestureBinding>> updateBindings(List<GestureBinding> bindings) async {
    final response = await _dio.put(
      ApiConfig.bindings,
      data: bindings.map((e) => e.toJson()).toList(),
    );
    return (response.data as List)
        .map((e) => GestureBinding.fromJson(e))
        .toList();
  }
  
  /// Add a gesture binding
  Future<GestureBinding> addBinding(GestureBinding binding) async {
    final response = await _dio.post(
      ApiConfig.bindings,
      data: binding.toJson(),
    );
    return GestureBinding.fromJson(response.data);
  }
  
  /// Delete a gesture binding
  Future<void> deleteBinding(String gesture) async {
    await _dio.delete('${ApiConfig.bindings}/$gesture');
  }
  
  // ============================================================================
  // Camera
  // ============================================================================
  
  /// List available cameras
  Future<List<CameraInfo>> listCameras() async {
    final response = await _dio.get(ApiConfig.cameras);
    return (response.data as List)
        .map((e) => CameraInfo.fromJson(e))
        .toList();
  }
  
  /// Select a camera
  Future<void> selectCamera(int index) async {
    await _dio.post('${ApiConfig.cameras}/select/$index');
  }
  
  /// Test if a camera is accessible
  Future<bool> testCamera(int index) async {
    final response = await _dio.post('${ApiConfig.cameras}/test/$index');
    return response.data['accessible'] == true;
  }
  
  // ============================================================================
  // Control
  // ============================================================================
  
  /// Get application status
  Future<AppStatus> getStatus() async {
    final response = await _dio.get(ApiConfig.status);
    return AppStatus.fromJson(response.data);
  }
  
  /// Start tracking
  Future<void> startTracking() async {
    await _dio.post('${ApiConfig.control}/start');
  }
  
  /// Stop tracking
  Future<void> stopTracking() async {
    await _dio.post('${ApiConfig.control}/stop');
  }
  
  /// Pause tracking
  Future<void> pauseTracking() async {
    await _dio.post('${ApiConfig.control}/pause');
  }
  
  /// Resume tracking
  Future<void> resumeTracking() async {
    await _dio.post('${ApiConfig.control}/resume');
  }
  
  /// Toggle pause state
  Future<bool> toggleTracking() async {
    final response = await _dio.post('${ApiConfig.control}/toggle');
    return response.data['paused'] == true;
  }
}
