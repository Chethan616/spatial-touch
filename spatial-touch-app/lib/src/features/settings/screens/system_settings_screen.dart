import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../providers/settings_provider.dart';
import '../widgets/settings_slider.dart';
import '../widgets/settings_switch.dart';
import '../widgets/section_header.dart';

class SystemSettingsScreen extends ConsumerWidget {
  const SystemSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);
    
    return settingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (settings) {
        final system = settings.system;
        
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'System Settings',
              subtitle: 'Application behavior and performance settings',
              icon: Icons.settings_rounded,
            ),
            const Gap(24),
            
            // Debug Mode
            SettingsSwitch(
              title: 'Debug Mode',
              description: 'Show debug overlay and verbose logging',
              value: system.debugMode,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateSystem(
                  system.copyWith(debugMode: value),
                );
              },
            ),
            const Gap(12),
            
            // Run on Startup
            SettingsSwitch(
              title: 'Run on Startup',
              description: 'Automatically start Spatial Touch when Windows starts',
              value: system.runOnStartup,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateSystem(
                  system.copyWith(runOnStartup: value),
                );
              },
            ),
            const Gap(12),
            
            // Show Tray Icon
            SettingsSwitch(
              title: 'Show System Tray Icon',
              description: 'Display icon in Windows system tray',
              value: system.showTrayIcon,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateSystem(
                  system.copyWith(showTrayIcon: value),
                );
              },
            ),
            const Gap(24),
            
            // Active FPS
            SettingsSlider(
              title: 'Active FPS',
              description: 'Frame rate when hand is detected',
              value: system.activeFps.toDouble(),
              min: 15,
              max: 60,
              divisions: 9,
              suffix: ' FPS',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateSystem(
                  system.copyWith(activeFps: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Idle FPS
            SettingsSlider(
              title: 'Idle FPS',
              description: 'Frame rate when no hand is detected (saves CPU)',
              value: system.idleFps.toDouble(),
              min: 1,
              max: 15,
              divisions: 14,
              suffix: ' FPS',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateSystem(
                  system.copyWith(idleFps: value.round()),
                );
              },
            ),
            const Gap(24),
            
            // Log Level
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Log Level',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Gap(4),
                    Text(
                      'Logging verbosity for troubleshooting',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const Gap(16),
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'DEBUG', label: Text('Debug')),
                        ButtonSegment(value: 'INFO', label: Text('Info')),
                        ButtonSegment(value: 'WARNING', label: Text('Warning')),
                        ButtonSegment(value: 'ERROR', label: Text('Error')),
                      ],
                      selected: {system.logLevel},
                      onSelectionChanged: (values) {
                        ref.read(settingsProvider.notifier).updateSystem(
                          system.copyWith(logLevel: values.first),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
            const Gap(32),
            
            // Version Info
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                        const Gap(12),
                        Text(
                          'About Spatial Touch',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const Gap(12),
                    _InfoRow(label: 'Version', value: '0.1.0'),
                    _InfoRow(label: 'Python Backend', value: 'Running'),
                    _InfoRow(label: 'API Port', value: '8765'),
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

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Text(value, style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w500,
          )),
        ],
      ),
    );
  }
}
