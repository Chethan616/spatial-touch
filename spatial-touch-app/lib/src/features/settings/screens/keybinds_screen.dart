import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../../../core/theme/app_theme.dart';
import '../providers/settings_provider.dart';
import '../models/settings_models.dart';
import '../widgets/section_header.dart';

class KeybindsScreen extends ConsumerStatefulWidget {
  const KeybindsScreen({super.key});

  @override
  ConsumerState<KeybindsScreen> createState() => _KeybindsScreenState();
}

class _KeybindsScreenState extends ConsumerState<KeybindsScreen> {
  @override
  Widget build(BuildContext context) {
    final bindingsAsync = ref.watch(bindingsProvider);
    
    return bindingsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (bindings) {
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SectionHeader(
              title: 'Custom Keybinds',
              subtitle: 'Configure gesture-to-action mappings',
              icon: Icons.keyboard_rounded,
            ),
            const Gap(24),
            
            // Add Binding Button
            Row(
              children: [
                FilledButton.icon(
                  onPressed: () => _showAddBindingDialog(context, ref),
                  icon: const Icon(Icons.add),
                  label: const Text('Add Keybind'),
                ),
                const Gap(12),
                OutlinedButton.icon(
                  onPressed: () => ref.read(bindingsProvider.notifier).refresh(),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Refresh'),
                ),
              ],
            ),
            const Gap(24),
            
            // Bindings List
            if (bindings.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    children: [
                      Icon(
                        Icons.keyboard_hide,
                        size: 48,
                        color: Theme.of(context).colorScheme.outline,
                      ),
                      const Gap(16),
                      Text(
                        'No custom keybinds',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const Gap(8),
                      Text(
                        'Add a keybind to map gestures to actions',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
              )
            else
              ...bindings.map((binding) => _BindingCard(
                binding: binding,
                onToggle: (enabled) {
                  ref.read(bindingsProvider.notifier).toggleBinding(
                    binding.gesture,
                    enabled,
                  );
                },
                onDelete: () {
                  ref.read(bindingsProvider.notifier).removeBinding(binding.gesture);
                },
                onEdit: () => _showEditBindingDialog(context, ref, binding),
              )),
            
            const Gap(32),
            
            // Available Gestures Reference
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Available Gestures',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Gap(16),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _GestureChip('pinch'),
                        _GestureChip('pinch_hold'),
                        _GestureChip('pinch_release'),
                        _GestureChip('double_tap'),
                        _GestureChip('swipe_up'),
                        _GestureChip('swipe_down'),
                        _GestureChip('swipe_left'),
                        _GestureChip('swipe_right'),
                        _GestureChip('open_palm'),
                        _GestureChip('fist'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const Gap(16),
            
            // Action Types Reference
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Action Types',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Gap(16),
                    _ActionTypeInfo(
                      type: 'key',
                      description: 'Keyboard shortcut (e.g., ctrl+c, alt+tab)',
                      example: 'ctrl+shift+esc',
                    ),
                    const Divider(height: 24),
                    _ActionTypeInfo(
                      type: 'mouse',
                      description: 'Mouse action',
                      example: 'left_click, right_click, double_click, scroll_up',
                    ),
                    const Divider(height: 24),
                    _ActionTypeInfo(
                      type: 'command',
                      description: 'System command to execute',
                      example: 'notepad.exe',
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
  
  void _showAddBindingDialog(BuildContext context, WidgetRef ref) {
    final gestureController = TextEditingController();
    final valueController = TextEditingController();
    String actionType = 'key';
    
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Add Keybind'),
          content: SizedBox(
            width: 400,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: 'pinch',
                  decoration: const InputDecoration(
                    labelText: 'Gesture',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'pinch', child: Text('Pinch')),
                    DropdownMenuItem(value: 'pinch_hold', child: Text('Pinch Hold')),
                    DropdownMenuItem(value: 'double_tap', child: Text('Double Tap')),
                    DropdownMenuItem(value: 'swipe_up', child: Text('Swipe Up')),
                    DropdownMenuItem(value: 'swipe_down', child: Text('Swipe Down')),
                    DropdownMenuItem(value: 'swipe_left', child: Text('Swipe Left')),
                    DropdownMenuItem(value: 'swipe_right', child: Text('Swipe Right')),
                    DropdownMenuItem(value: 'open_palm', child: Text('Open Palm')),
                    DropdownMenuItem(value: 'fist', child: Text('Fist')),
                  ],
                  onChanged: (value) {
                    gestureController.text = value ?? 'pinch';
                  },
                ),
                const Gap(16),
                DropdownButtonFormField<String>(
                  value: actionType,
                  decoration: const InputDecoration(
                    labelText: 'Action Type',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'key', child: Text('Keyboard Shortcut')),
                    DropdownMenuItem(value: 'mouse', child: Text('Mouse Action')),
                    DropdownMenuItem(value: 'command', child: Text('Command')),
                  ],
                  onChanged: (value) {
                    setState(() => actionType = value ?? 'key');
                  },
                ),
                const Gap(16),
                if (actionType == 'mouse')
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Mouse Action',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'left_click', child: Text('Left Click')),
                      DropdownMenuItem(value: 'right_click', child: Text('Right Click')),
                      DropdownMenuItem(value: 'double_click', child: Text('Double Click')),
                      DropdownMenuItem(value: 'middle_click', child: Text('Middle Click')),
                      DropdownMenuItem(value: 'scroll_up', child: Text('Scroll Up')),
                      DropdownMenuItem(value: 'scroll_down', child: Text('Scroll Down')),
                    ],
                    onChanged: (value) {
                      valueController.text = value ?? '';
                    },
                  )
                else
                  TextField(
                    controller: valueController,
                    decoration: InputDecoration(
                      labelText: actionType == 'key' ? 'Key Combination' : 'Command',
                      hintText: actionType == 'key' ? 'ctrl+alt+tab' : 'notepad.exe',
                      border: const OutlineInputBorder(),
                    ),
                  ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () {
                if (gestureController.text.isNotEmpty || valueController.text.isNotEmpty) {
                  ref.read(bindingsProvider.notifier).addBinding(
                    GestureBinding(
                      gesture: gestureController.text.isEmpty ? 'pinch' : gestureController.text,
                      action: actionType,
                      value: valueController.text,
                    ),
                  );
                  Navigator.pop(context);
                }
              },
              child: const Text('Add'),
            ),
          ],
        ),
      ),
    );
  }
  
  void _showEditBindingDialog(BuildContext context, WidgetRef ref, GestureBinding binding) {
    final valueController = TextEditingController(text: binding.value);
    String actionType = binding.action;
    
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text('Edit ${binding.gesture}'),
          content: SizedBox(
            width: 400,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: actionType,
                  decoration: const InputDecoration(
                    labelText: 'Action Type',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'key', child: Text('Keyboard Shortcut')),
                    DropdownMenuItem(value: 'mouse', child: Text('Mouse Action')),
                    DropdownMenuItem(value: 'command', child: Text('Command')),
                  ],
                  onChanged: (value) {
                    setState(() => actionType = value ?? 'key');
                  },
                ),
                const Gap(16),
                TextField(
                  controller: valueController,
                  decoration: InputDecoration(
                    labelText: actionType == 'key' ? 'Key Combination' : 
                               actionType == 'mouse' ? 'Mouse Action' : 'Command',
                    border: const OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () {
                final bindings = ref.read(bindingsProvider).valueOrNull ?? [];
                final updated = bindings.map((b) {
                  if (b.gesture == binding.gesture) {
                    return b.copyWith(action: actionType, value: valueController.text);
                  }
                  return b;
                }).toList();
                ref.read(bindingsProvider.notifier).updateBindings(updated);
                Navigator.pop(context);
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }
}

class _BindingCard extends StatelessWidget {
  final GestureBinding binding;
  final ValueChanged<bool> onToggle;
  final VoidCallback onDelete;
  final VoidCallback onEdit;

  const _BindingCard({
    required this.binding,
    required this.onToggle,
    required this.onDelete,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // Enable Toggle
            Switch(
              value: binding.enabled,
              onChanged: onToggle,
            ),
            const Gap(12),
            
            // Gesture Icon & Name
            Container(
              width: 120,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _formatGestureName(binding.gesture),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: binding.enabled ? null : Theme.of(context).disabledColor,
                    ),
                  ),
                  Text(
                    binding.gesture,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.outline,
                    ),
                  ),
                ],
              ),
            ),
            const Gap(16),
            
            // Arrow
            Icon(
              Icons.arrow_forward,
              color: Theme.of(context).colorScheme.outline,
            ),
            const Gap(16),
            
            // Action
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _ActionChip(type: binding.action),
                  const Gap(4),
                  Text(
                    binding.value,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontFamily: 'monospace',
                      color: binding.enabled ? null : Theme.of(context).disabledColor,
                    ),
                  ),
                ],
              ),
            ),
            
            // Actions
            IconButton(
              icon: const Icon(Icons.edit_outlined),
              onPressed: onEdit,
              tooltip: 'Edit',
            ),
            IconButton(
              icon: Icon(Icons.delete_outline, color: Theme.of(context).colorScheme.error),
              onPressed: onDelete,
              tooltip: 'Delete',
            ),
          ],
        ),
      ),
    );
  }
  
  String _formatGestureName(String gesture) {
    return gesture.split('_').map((word) => 
      word[0].toUpperCase() + word.substring(1)
    ).join(' ');
  }
}

class _GestureChip extends StatelessWidget {
  final String gesture;

  const _GestureChip(this.gesture);

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(gesture),
      backgroundColor: AppTheme.primaryColor.withAlpha(25),
      labelStyle: TextStyle(
        color: AppTheme.primaryColor,
        fontSize: 12,
      ),
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
}

class _ActionChip extends StatelessWidget {
  final String type;

  const _ActionChip({required this.type});

  @override
  Widget build(BuildContext context) {
    Color color;
    IconData icon;
    
    switch (type) {
      case 'key':
        color = AppTheme.primaryColor;
        icon = Icons.keyboard;
        break;
      case 'mouse':
        color = AppTheme.secondaryColor;
        icon = Icons.mouse;
        break;
      case 'command':
        color = AppTheme.accentColor;
        icon = Icons.terminal;
        break;
      default:
        color = Colors.grey;
        icon = Icons.help_outline;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const Gap(4),
          Text(
            type.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionTypeInfo extends StatelessWidget {
  final String type;
  final String description;
  final String example;

  const _ActionTypeInfo({
    required this.type,
    required this.description,
    required this.example,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _ActionChip(type: type),
        const Gap(8),
        Text(description, style: Theme.of(context).textTheme.bodyMedium),
        const Gap(4),
        Text(
          'Example: $example',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            fontFamily: 'monospace',
            color: Theme.of(context).colorScheme.outline,
          ),
        ),
      ],
    );
  }
}
