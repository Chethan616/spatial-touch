import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../providers/settings_provider.dart';
import '../widgets/settings_slider.dart';
import '../widgets/section_header.dart';

class GestureSettingsScreen extends ConsumerWidget {
  const GestureSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);
    
    return settingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (settings) {
        final gestures = settings.gestures;
        
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'Gesture Detection',
              subtitle: 'Fine-tune how gestures are recognized',
              icon: Icons.gesture_rounded,
            ),
            const Gap(24),
            
            // Pinch Threshold
            SettingsSlider(
              title: 'Pinch Threshold',
              description: 'Distance between thumb and index finger to trigger pinch',
              value: gestures.pinchThreshold,
              min: 0.01,
              max: 0.15,
              divisions: 14,
              suffix: '',
              decimals: 2,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateGestures(
                  gestures.copyWith(pinchThreshold: value),
                );
              },
            ),
            const Gap(16),
            
            // Debounce Time
            SettingsSlider(
              title: 'Debounce Time',
              description: 'Time to wait between gesture triggers',
              value: gestures.debounceMs.toDouble(),
              min: 50,
              max: 500,
              divisions: 9,
              suffix: ' ms',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateGestures(
                  gestures.copyWith(debounceMs: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Hold Time
            SettingsSlider(
              title: 'Hold Time',
              description: 'Time to hold gesture for long press',
              value: gestures.holdTimeMs.toDouble(),
              min: 100,
              max: 1000,
              divisions: 18,
              suffix: ' ms',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateGestures(
                  gestures.copyWith(holdTimeMs: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Click Release Time
            SettingsSlider(
              title: 'Click Release Time',
              description: 'Maximum time between press and release for a click',
              value: gestures.clickReleaseMs.toDouble(),
              min: 50,
              max: 500,
              divisions: 9,
              suffix: ' ms',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateGestures(
                  gestures.copyWith(clickReleaseMs: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Velocity Threshold
            SettingsSlider(
              title: 'Velocity Threshold',
              description: 'Minimum speed for swipe gesture detection',
              value: gestures.velocityThreshold,
              min: 0.0,
              max: 0.1,
              divisions: 20,
              suffix: '',
              decimals: 3,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateGestures(
                  gestures.copyWith(velocityThreshold: value),
                );
              },
            ),
            const Gap(32),
            
            // Gesture Preview Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Gesture Types',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Gap(16),
                    _GestureItem(
                      icon: Icons.touch_app,
                      name: 'Pinch',
                      description: 'Touch thumb to index finger',
                    ),
                    const Divider(height: 24),
                    _GestureItem(
                      icon: Icons.touch_app,
                      name: 'Pinch Hold',
                      description: 'Hold pinch for drag operations',
                    ),
                    const Divider(height: 24),
                    _GestureItem(
                      icon: Icons.ads_click,
                      name: 'Double Tap',
                      description: 'Two quick pinches',
                    ),
                    const Divider(height: 24),
                    _GestureItem(
                      icon: Icons.swipe,
                      name: 'Swipe',
                      description: 'Quick directional hand movement',
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _GestureItem extends StatelessWidget {
  final IconData icon;
  final String name;
  final String description;

  const _GestureItem({
    required this.icon,
    required this.name,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 24, color: Theme.of(context).colorScheme.primary),
        const Gap(12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name, style: Theme.of(context).textTheme.titleSmall),
              Text(description, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
      ],
    );
  }
}
