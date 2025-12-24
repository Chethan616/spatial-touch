import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/api_config.dart';

/// WebSocket connection state
enum WebSocketState {
  disconnected,
  connecting,
  connected,
  error,
}

/// WebSocket event
class WebSocketEvent {
  final String event;
  final Map<String, dynamic> data;
  
  WebSocketEvent({required this.event, required this.data});
  
  factory WebSocketEvent.fromJson(Map<String, dynamic> json) {
    return WebSocketEvent(
      event: json['event'] as String,
      data: json['data'] as Map<String, dynamic>,
    );
  }
}

/// WebSocket service provider
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  ref.onDispose(() => service.disconnect());
  return service;
});

/// WebSocket state provider
final webSocketStateProvider = StateProvider<WebSocketState>((ref) {
  return WebSocketState.disconnected;
});

/// WebSocket service for real-time updates
class WebSocketService {
  WebSocketChannel? _channel;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  final StreamController<WebSocketEvent> _eventController = StreamController.broadcast();
  
  /// Stream of WebSocket events
  Stream<WebSocketEvent> get events => _eventController.stream;
  
  /// Current connection state
  WebSocketState state = WebSocketState.disconnected;
  
  /// Connect to WebSocket server
  Future<void> connect({Function(WebSocketState)? onStateChange}) async {
    if (state == WebSocketState.connecting || state == WebSocketState.connected) {
      return;
    }
    
    state = WebSocketState.connecting;
    onStateChange?.call(state);
    
    try {
      _channel = WebSocketChannel.connect(Uri.parse(ApiConfig.wsUrl));
      
      _channel!.stream.listen(
        (message) {
          try {
            final json = jsonDecode(message);
            final event = WebSocketEvent.fromJson(json);
            _eventController.add(event);
          } catch (e) {
            // Handle ping/pong
            if (message == 'pong') return;
            print('WebSocket parse error: $e');
          }
        },
        onDone: () {
          state = WebSocketState.disconnected;
          onStateChange?.call(state);
          _scheduleReconnect(onStateChange);
        },
        onError: (error) {
          state = WebSocketState.error;
          onStateChange?.call(state);
          _scheduleReconnect(onStateChange);
        },
      );
      
      state = WebSocketState.connected;
      onStateChange?.call(state);
      
      // Start ping timer for keep-alive
      _startPingTimer();
      
    } catch (e) {
      state = WebSocketState.error;
      onStateChange?.call(state);
      _scheduleReconnect(onStateChange);
    }
  }
  
  /// Disconnect from WebSocket server
  void disconnect() {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
    state = WebSocketState.disconnected;
  }
  
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (state == WebSocketState.connected) {
        _channel?.sink.add('ping');
      }
    });
  }
  
  void _scheduleReconnect(Function(WebSocketState)? onStateChange) {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 5), () {
      connect(onStateChange: onStateChange);
    });
  }
  
  void dispose() {
    disconnect();
    _eventController.close();
  }
}
