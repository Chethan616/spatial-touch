import 'package:flutter/material.dart';
import 'package:gap/gap.dart';
import '../../../core/theme/app_theme.dart';
import '../home_screen.dart';

class NavRail extends StatelessWidget {
  final List<NavItem> items;
  final int selectedIndex;
  final ValueChanged<int> onSelect;

  const NavRail({
    super.key,
    required this.items,
    required this.selectedIndex,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        final isSelected = index == selectedIndex;
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: _NavItem(
            item: item,
            isSelected: isSelected,
            onTap: () => onSelect(index),
          ),
        );
      },
    );
  }
}

class _NavItem extends StatelessWidget {
  final NavItem item;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavItem({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: isSelected 
          ? AppTheme.primaryColor.withAlpha(25)
          : Colors.transparent,
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            children: [
              Icon(
                isSelected ? item.selectedIcon : item.icon,
                size: 22,
                color: isSelected 
                    ? AppTheme.primaryColor 
                    : Theme.of(context).textTheme.bodyMedium?.color,
              ),
              const Gap(12),
              Text(
                item.label,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                  color: isSelected 
                      ? AppTheme.primaryColor 
                      : Theme.of(context).textTheme.titleMedium?.color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
