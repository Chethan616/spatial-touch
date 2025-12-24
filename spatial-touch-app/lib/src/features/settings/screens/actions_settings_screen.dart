import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../providers/settings_provider.dart';
import '../widgets/settings_slider.dart';
import '../widgets/settings_switch.dart';
import '../widgets/section_header.dart';

class ActionsSettingsScreen extends ConsumerWidget {
  const ActionsSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);
    
    return settingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (settings) {
        final actions = settings.actions;
        
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'Action Settings',
              subtitle: 'Configure mouse and keyboard input behavior',
              icon: Icons.touch_app_rounded,
            ),
            const Gap(24),
            
            // Enable Mouse
            SettingsSwitch(
              title: 'Enable Mouse Control',
              description: 'Allow gestures to control the mouse cursor',
              value: actions.enableMouse,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateActions(
                  actions.copyWith(enableMouse: value),
                );
              },
            ),
            const Gap(12),
            
            // Enable Keyboard
            SettingsSwitch(
              title: 'Enable Keyboard Shortcuts',
              description: 'Allow gestures to trigger keyboard shortcuts',
              value: actions.enableKeyboard,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateActions(
                  actions.copyWith(enableKeyboard: value),
                );
              },
            ),
            const Gap(12),
            
            // Safe Mode
            SettingsSwitch(
              title: 'Safe Mode',
              description: 'Limit cursor speed and prevent accidental actions',
              value: actions.safeMode,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateActions(
                  actions.copyWith(safeMode: value),
                );
              },
            ),
            const Gap(24),
            
            // Mouse Movement Duration
            SettingsSlider(
              title: 'Mouse Movement Duration',
              description: 'Time for cursor to move to target (0 = instant)',
              value: actions.moveDuration,
              min: 0.0,
              max: 0.5,
              divisions: 10,
              suffix: ' sec',
              decimals: 2,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateActions(
                  actions.copyWith(moveDuration: value),
                );
              },
            ),
            const Gap(16),
            
            // Click Interval
            SettingsSlider(
              title: 'Click Interval',
              description: 'Minimum time between clicks',
              value: actions.clickInterval,
              min: 0.0,
              max: 0.5,
              divisions: 10,
              suffix: ' sec',
              decimals: 2,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateActions(
                  actions.copyWith(clickInterval: value),
                );
              },
            ),
            const Gap(16),
            
            // Scroll Amount
            SettingsSlider(
              title: 'Scroll Amount',
              description: 'Lines to scroll per gesture',
              value: actions.scrollAmount.toDouble(),
              min: 1,
              max: 10,
              divisions: 9,
              suffix: ' lines',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateActions(
                  actions.copyWith(scrollAmount: value.round()),
                );
              },
            ),
            const Gap(32),
            
            // Warning Card
            if (!actions.safeMode)
              Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(
                        Icons.warning_amber_rounded,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      const Gap(12),
                      Expanded(
                        child: Text(
                          'Safe mode is disabled. The cursor may move quickly and trigger unintended actions.',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Theme.of(context).colorScheme.onErrorContainer,
                          ),
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
