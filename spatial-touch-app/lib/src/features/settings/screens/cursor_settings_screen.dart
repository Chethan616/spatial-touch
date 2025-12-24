import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../providers/settings_provider.dart';
import '../widgets/settings_slider.dart';
import '../widgets/settings_switch.dart';
import '../widgets/section_header.dart';

class CursorSettingsScreen extends ConsumerWidget {
  const CursorSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);
    
    return settingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (settings) {
        final cursor = settings.cursor;
        
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'Cursor Control',
              subtitle: 'Customize cursor movement and mapping',
              icon: Icons.mouse_rounded,
            ),
            const Gap(24),
            
            // Sensitivity
            SettingsSlider(
              title: 'Sensitivity',
              description: 'How fast the cursor moves relative to hand movement',
              value: cursor.sensitivity,
              min: 0.5,
              max: 3.0,
              divisions: 25,
              suffix: 'x',
              decimals: 1,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCursor(
                  cursor.copyWith(sensitivity: value),
                );
              },
            ),
            const Gap(16),
            
            // Dead Zone
            SettingsSlider(
              title: 'Dead Zone',
              description: 'Area of no movement to prevent jitter',
              value: cursor.deadZone,
              min: 0.0,
              max: 0.1,
              divisions: 20,
              suffix: '',
              showPercentage: true,
              decimals: 2,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCursor(
                  cursor.copyWith(deadZone: value),
                );
              },
            ),
            const Gap(16),
            
            // Cursor Smoothing
            SettingsSlider(
              title: 'Cursor Smoothing',
              description: 'Additional smoothing for cursor movement',
              value: cursor.smoothing,
              min: 0.0,
              max: 1.0,
              divisions: 20,
              suffix: '',
              showPercentage: true,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCursor(
                  cursor.copyWith(smoothing: value),
                );
              },
            ),
            const Gap(16),
            
            // Screen Edge Margin
            SettingsSlider(
              title: 'Screen Edge Margin',
              description: 'Padding from screen edges in pixels',
              value: cursor.margin.toDouble(),
              min: 0,
              max: 100,
              divisions: 20,
              suffix: ' px',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCursor(
                  cursor.copyWith(margin: value.round()),
                );
              },
            ),
            const Gap(24),
            
            // Invert Controls
            Text(
              'Axis Inversion',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Gap(12),
            
            SettingsSwitch(
              title: 'Invert X Axis (Mirror Mode)',
              description: 'Mirror horizontal movement like looking in a mirror',
              value: cursor.invertX,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCursor(
                  cursor.copyWith(invertX: value),
                );
              },
            ),
            const Gap(12),
            
            SettingsSwitch(
              title: 'Invert Y Axis',
              description: 'Invert vertical movement direction',
              value: cursor.invertY,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateCursor(
                  cursor.copyWith(invertY: value),
                );
              },
            ),
            const Gap(32),
            
            // Tip Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const Gap(12),
                    Expanded(
                      child: Text(
                        'Mirror mode (Invert X) is recommended for most users as it feels more natural when looking at your screen.',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
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
