import 'package:flutter/material.dart';
import 'package:gap/gap.dart';
import '../../../core/theme/app_theme.dart';
import '../../settings/models/settings_models.dart';

class StatusCard extends StatelessWidget {
  final AppStatus status;
  final bool isConnected;
  final VoidCallback onStart;
  final VoidCallback onStop;
  final VoidCallback onToggle;

  const StatusCard({
    super.key,
    required this.status,
    required this.isConnected,
    required this.onStart,
    required this.onStop,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    final isRunning = status.running;
    final isPaused = status.paused;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).dividerTheme.color ?? Colors.grey.shade300,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: !isConnected
                      ? AppTheme.errorColor
                      : isRunning
                          ? (isPaused ? AppTheme.warningColor : AppTheme.successColor)
                          : Colors.grey,
                ),
              ),
              const Gap(8),
              Text(
                !isConnected
                    ? 'Disconnected'
                    : isRunning
                        ? (isPaused ? 'Paused' : 'Tracking')
                        : 'Stopped',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          if (isConnected && isRunning) ...[
            const Gap(8),
            Text(
              'FPS: ${status.fpsActual.toStringAsFixed(1)} | Frames: ${status.frameCount}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
          const Gap(12),
          Row(
            children: [
              Expanded(
                child: _ActionButton(
                  icon: isRunning ? Icons.stop_rounded : Icons.play_arrow_rounded,
                  label: isRunning ? 'Stop' : 'Start',
                  color: isRunning ? AppTheme.errorColor : AppTheme.successColor,
                  onPressed: isConnected ? (isRunning ? onStop : onStart) : null,
                ),
              ),
              if (isRunning) ...[
                const Gap(8),
                Expanded(
                  child: _ActionButton(
                    icon: isPaused ? Icons.play_arrow_rounded : Icons.pause_rounded,
                    label: isPaused ? 'Resume' : 'Pause',
                    color: AppTheme.primaryColor,
                    onPressed: onToggle,
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback? onPressed;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withAlpha(25),
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 18, color: color),
              const Gap(6),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
