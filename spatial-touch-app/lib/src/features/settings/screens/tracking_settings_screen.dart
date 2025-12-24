import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../providers/settings_provider.dart';
import '../widgets/settings_slider.dart';
import '../widgets/section_header.dart';

class TrackingSettingsScreen extends ConsumerWidget {
  const TrackingSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);
    
    return settingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (settings) {
        final tracking = settings.tracking;
        
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'Hand Tracking',
              subtitle: 'Configure MediaPipe hand detection parameters',
              icon: Icons.pan_tool_rounded,
            ),
            const Gap(24),
            
            // Max Hands
            SettingsSlider(
              title: 'Maximum Hands',
              description: 'Number of hands to track simultaneously',
              value: tracking.maxHands.toDouble(),
              min: 1,
              max: 2,
              divisions: 1,
              suffix: tracking.maxHands == 1 ? ' hand' : ' hands',
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateTracking(
                  tracking.copyWith(maxHands: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Detection Confidence
            SettingsSlider(
              title: 'Detection Confidence',
              description: 'Minimum confidence for detecting a hand',
              value: tracking.minDetectionConfidence,
              min: 0.1,
              max: 1.0,
              divisions: 18,
              suffix: '',
              showPercentage: true,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateTracking(
                  tracking.copyWith(minDetectionConfidence: value),
                );
              },
            ),
            const Gap(16),
            
            // Tracking Confidence
            SettingsSlider(
              title: 'Tracking Confidence',
              description: 'Minimum confidence for continued hand tracking',
              value: tracking.minTrackingConfidence,
              min: 0.1,
              max: 1.0,
              divisions: 18,
              suffix: '',
              showPercentage: true,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateTracking(
                  tracking.copyWith(minTrackingConfidence: value),
                );
              },
            ),
            const Gap(16),
            
            // Model Complexity
            SettingsSlider(
              title: 'Model Complexity',
              description: 'Higher complexity = better accuracy but slower',
              value: tracking.modelComplexity.toDouble(),
              min: 0,
              max: 2,
              divisions: 2,
              suffix: _getComplexityLabel(tracking.modelComplexity),
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateTracking(
                  tracking.copyWith(modelComplexity: value.round()),
                );
              },
            ),
            const Gap(16),
            
            // Smoothing Factor
            SettingsSlider(
              title: 'Smoothing Factor',
              description: 'Higher values = smoother but more delayed tracking',
              value: tracking.smoothingFactor,
              min: 0.0,
              max: 1.0,
              divisions: 20,
              suffix: '',
              showPercentage: true,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateTracking(
                  tracking.copyWith(smoothingFactor: value),
                );
              },
            ),
            const Gap(32),
            
            // Info Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const Gap(12),
                    Expanded(
                      child: Text(
                        'Lower detection confidence catches hands faster but may have false positives. Higher tracking confidence reduces jitter but may lose tracking more easily.',
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
  
  String _getComplexityLabel(int complexity) {
    switch (complexity) {
      case 0:
        return ' (Lite)';
      case 1:
        return ' (Full)';
      case 2:
        return ' (Heavy)';
      default:
        return '';
    }
  }
}
