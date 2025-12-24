/// API configuration
class ApiConfig {
  static const String baseUrl = 'http://localhost:8765';
  static const String wsUrl = 'ws://localhost:8765/ws';
  static const Duration timeout = Duration(seconds: 10);
  
  // Endpoints
  static const String settings = '/api/settings';
  static const String bindings = '/api/bindings';
  static const String cameras = '/api/cameras';
  static const String status = '/api/status';
  static const String control = '/api/control';
}
