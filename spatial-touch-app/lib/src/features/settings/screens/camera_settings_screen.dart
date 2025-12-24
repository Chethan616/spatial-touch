import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../providers/settings_provider.dart';
import '../models/settings_models.dart';
import '../widgets/settings_card.dart';
import '../widgets/settings_slider.dart';
import '../widgets/settings_switch.dart';
import '../widgets/section_header.dart';

class CameraSettingsScreen extends ConsumerWidget {
  const CameraSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);
    final camerasAsync = ref.watch(camerasProvider);
    
    return settingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (settings) {
        final camera = settings.camera;
        
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'Camera Settings',
              subtitle: 'Configure your webcam for hand tracking',
              icon: Icons.videocam_rounded,
            ),
            const Gap(24),
            
            // Camera Selection
            SettingsCard(
              title: 'Camera Device',
              description: 'Select which camera to use for tracking',
              child: camerasAsync.when(
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (e, _) => Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text('Failed to load cameras: $e'),
                ),
                data: (cameras) {
                  if (cameras.isEmpty) {
                    return const Padding(
                      padding: EdgeInsets.all(16),
                      child: Text('No cameras detected'),
                    );
                  }
                  
                  return Column(
                    children: cameras.map((cam) {
                      return RadioListTile<int>(
                        value: cam.index,
                        groupValue: camera.deviceIndex,
                        title: Text(cam.name),
                        subtitle: Text(
                          'Resolutions: ${cam.resolutions.map((r) => '${r[0]}x${r[1]}').join(', ')}',
                        ),
                        onChanged: (value) {
                          if (value != null) {
                            ref.read(settingsProvider.notifier).updateCamera(
                              camera.copyWith(deviceIndex: value),
                            );
                          }
                        },
                      );
                    }).toList(),
                  );
                },
              ),
            ),
            const Gap(16),
            
            // Resolution
            SettingsCard(
              title: 'Resolution',
              description: 'Camera capture resolution',
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: DropdownButtonFormField<String>(
                  value: '${camera.resolution[0]}x${camera.resolution[1]}',
                  decoration: const InputDecoration(
                    labelText: 'Resolution',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: '640x480', child: Text('640 x 480 (VGA)')),
                    DropdownMenuItem(value: '1280x720', child: Text('1280 x 720 (HD)')),
                    DropdownMenuItem(value: '1920x1080', child: Text('1920 x 1080 (Full HD)')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      final parts = value.split('x');
                      ref.read(settingsProvider.notifier).updateCamera(
                        camera.copyWith(
                          resolution: [int.parse(parts[0]), int.parse(parts[1])],
                        ),
                      );
                    }
                  },
                ),
              ),
            ),
            const Gap(16),
            
            // FPS
            SettingsSlider(
              title: 'Frame Rate (FPS)',
              description: 'Camera capture frame rate',
              value: camera.fps.toDouble(),
              min: 15,
              max: 60,
              divisions: 9,
              suffix: ' FPS',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCamera(
                  camera.copyWith(fps: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Auto Reconnect
            SettingsSwitch(
              title: 'Auto Reconnect',
              description: 'Automatically reconnect if camera disconnects',
              value: camera.autoReconnect,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCamera(
                  camera.copyWith(autoReconnect: value),
                );
              },
            ),
            const Gap(16),
            
            // Reconnect Delay
            if (camera.autoReconnect)
              SettingsSlider(
                title: 'Reconnect Delay',
                description: 'Time to wait before attempting reconnection',
                value: camera.reconnectDelay,
                min: 0.5,
                max: 10.0,
                divisions: 19,
                suffix: ' sec',
                onChanged: (value) {
                  ref.read(settingsProvider.notifier).updateCamera(
                    camera.copyWith(reconnectDelay: value),
                  );
                },
              ),
            const Gap(16),
            
            // Warmup Frames
            SettingsSlider(
              title: 'Warmup Frames',
              description: 'Frames to skip during camera initialization',
              value: camera.warmupFrames.toDouble(),
              min: 0,
              max: 50,
              divisions: 10,
              suffix: ' frames',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCamera(
                  camera.copyWith(warmupFrames: value.round()),
                );
              },
            ),
            const Gap(32),
            
            // Refresh Button
            Center(
              child: FilledButton.icon(
                onPressed: () => ref.invalidate(camerasProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh Cameras'),
              ),
            ),
          ],
        );
      },
    );
  }
}
