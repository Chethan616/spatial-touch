import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:gap/gap.dart';

import '../../core/theme/app_theme.dart';
import '../../core/providers/theme_provider.dart';
import '../settings/providers/settings_provider.dart';
import 'widgets/status_card.dart';
import 'widgets/nav_rail.dart';
import '../settings/screens/camera_settings_screen.dart';
import '../settings/screens/tracking_settings_screen.dart';
import '../settings/screens/gesture_settings_screen.dart';
import '../settings/screens/cursor_settings_screen.dart';
import '../settings/screens/actions_settings_screen.dart';
import '../settings/screens/keybinds_screen.dart';
import '../settings/screens/system_settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _selectedIndex = 0;
  
  final List<NavItem> _navItems = [
    NavItem(icon: Icons.videocam_outlined, selectedIcon: Icons.videocam, label: 'Camera'),
    NavItem(icon: Icons.pan_tool_outlined, selectedIcon: Icons.pan_tool, label: 'Tracking'),
    NavItem(icon: Icons.gesture_outlined, selectedIcon: Icons.gesture, label: 'Gestures'),
    NavItem(icon: Icons.mouse_outlined, selectedIcon: Icons.mouse, label: 'Cursor'),
    NavItem(icon: Icons.touch_app_outlined, selectedIcon: Icons.touch_app, label: 'Actions'),
    NavItem(icon: Icons.keyboard_outlined, selectedIcon: Icons.keyboard, label: 'Keybinds'),
    NavItem(icon: Icons.settings_outlined, selectedIcon: Icons.settings, label: 'System'),
  ];
  
  Widget _getScreen(int index) {
    switch (index) {
      case 0:
        return const CameraSettingsScreen();
      case 1:
        return const TrackingSettingsScreen();
      case 2:
        return const GestureSettingsScreen();
      case 3:
        return const CursorSettingsScreen();
      case 4:
        return const ActionsSettingsScreen();
      case 5:
        return const KeybindsScreen();
      case 6:
        return const SystemSettingsScreen();
      default:
        return const CameraSettingsScreen();
    }
  }

  @override
  void initState() {
    super.initState();
    // Initial load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(settingsProvider.notifier).refresh();
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = ref.watch(isDarkModeProvider);
    final isConnected = ref.watch(connectionStatusProvider);
    final appStatus = ref.watch(appStatusProvider);
    
    return Scaffold(
      body: Row(
        children: [
          // Navigation Rail
          Container(
            width: 220,
            decoration: BoxDecoration(
              color: Theme.of(context).cardTheme.color,
              border: Border(
                right: BorderSide(
                  color: isDarkMode ? AppTheme.borderDark : AppTheme.borderLight,
                ),
              ),
            ),
            child: Column(
              children: [
                const Gap(24),
                // App Title
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.pan_tool_alt_rounded,
                          color: Colors.white,
                          size: 24,
                        ),
                      ),
                      const Gap(12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Spatial Touch',
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            Text(
                              isConnected ? 'Connected' : 'Disconnected',
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: isConnected ? AppTheme.successColor : AppTheme.errorColor,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const Gap(32),
                
                // Navigation Items
                Expanded(
                  child: NavRail(
                    items: _navItems,
                    selectedIndex: _selectedIndex,
                    onSelect: (index) {
                      setState(() => _selectedIndex = index);
                    },
                  ),
                ),
                
                // Status Card
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: StatusCard(
                    status: appStatus,
                    isConnected: isConnected,
                    onStart: () => ref.read(appStatusProvider.notifier).start(),
                    onStop: () => ref.read(appStatusProvider.notifier).stop(),
                    onToggle: () => ref.read(appStatusProvider.notifier).toggle(),
                  ),
                ),
                
                // Theme Toggle
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.light_mode_outlined,
                        size: 20,
                        color: !isDarkMode ? AppTheme.primaryColor : null,
                      ),
                      const Gap(8),
                      Switch(
                        value: isDarkMode,
                        onChanged: (_) => ref.read(isDarkModeProvider.notifier).toggle(),
                      ),
                      const Gap(8),
                      Icon(
                        Icons.dark_mode_outlined,
                        size: 20,
                        color: isDarkMode ? AppTheme.primaryColor : null,
                      ),
                    ],
                  ),
                ),
                const Gap(8),
              ],
            ),
          ),
          
          // Main Content
          Expanded(
            child: _getScreen(_selectedIndex),
          ),
        ],
      ),
    );
  }
}

class NavItem {
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  
  NavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
  });
}
