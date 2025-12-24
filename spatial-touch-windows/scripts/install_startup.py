"""
Startup Installation Script

Configures Spatial Touch to run on Windows startup.
"""

import os
import sys
import winreg
import argparse
from pathlib import Path


APP_NAME = "SpatialTouch"
REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_exe_path() -> str:
    """Get path to the executable."""
    # Check common locations
    possible_paths = [
        Path(__file__).parent.parent / "dist" / "SpatialTouch.exe",
        Path(sys.executable).parent / "SpatialTouch.exe",
        Path.cwd() / "dist" / "SpatialTouch.exe",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path.absolute())
    
    return None


def add_to_startup(exe_path: str) -> bool:
    """Add application to Windows startup.
    
    Args:
        exe_path: Path to the executable
        
    Returns:
        True if successful
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print(f"✅ Added to startup: {exe_path}")
        return True
    except WindowsError as e:
        print(f"❌ Failed to add to startup: {e}")
        return False


def remove_from_startup() -> bool:
    """Remove application from Windows startup.
    
    Returns:
        True if successful
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print("✅ Removed from startup")
        return True
    except WindowsError as e:
        print(f"❌ Failed to remove from startup: {e}")
        return False


def check_startup_status() -> bool:
    """Check if application is in startup.
    
    Returns:
        True if in startup
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"✅ Startup enabled: {value}")
        return True
    except WindowsError:
        print("ℹ️ Startup not configured")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Configure Spatial Touch to run on Windows startup"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add to startup')
    add_parser.add_argument(
        '--path', '-p',
        type=str,
        help='Path to executable (auto-detected if not specified)'
    )
    
    # Remove command
    subparsers.add_parser('remove', help='Remove from startup')
    
    # Status command
    subparsers.add_parser('status', help='Check startup status')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Spatial Touch Startup Configuration")
    print("=" * 50)
    
    if args.command == 'add':
        exe_path = args.path or get_exe_path()
        if not exe_path:
            print("❌ Executable not found. Please specify path with --path")
            sys.exit(1)
        if not os.path.exists(exe_path):
            print(f"❌ Executable not found: {exe_path}")
            sys.exit(1)
        add_to_startup(exe_path)
        
    elif args.command == 'remove':
        remove_from_startup()
        
    elif args.command == 'status':
        check_startup_status()
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
