"""
Build Script for Spatial Touch

Creates a standalone executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """Remove old build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/...")
            shutil.rmtree(dir_name)
    
    # Remove .spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing {spec_file}...")
        spec_file.unlink()


def create_executable():
    """Create executable using PyInstaller."""
    print("Building Spatial Touch executable...")
    
    # PyInstaller command
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'SpatialTouch',
        '--icon', 'docs/assets/icon.ico',
        '--add-data', 'config;config',
        '--hidden-import', 'mediapipe',
        '--hidden-import', 'cv2',
        '--hidden-import', 'pyautogui',
        '--hidden-import', 'pynput',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'tkinter',
        '--exclude-module', 'pytest',
        'src/spatial_touch/main.py',
    ]
    
    # Check if icon exists
    if not os.path.exists('docs/assets/icon.ico'):
        cmd.remove('--icon')
        cmd.remove('docs/assets/icon.ico')
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build successful!")
        print(f"   Executable: dist/SpatialTouch.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False
    
    return True


def copy_config_files():
    """Copy configuration files to dist folder."""
    dist_config = Path('dist/config')
    dist_config.mkdir(exist_ok=True)
    
    for config_file in Path('config').glob('*.json'):
        shutil.copy(config_file, dist_config)
        print(f"Copied {config_file} to dist/config/")


def main():
    """Main build function."""
    print("=" * 50)
    print("Spatial Touch Build Script")
    print("=" * 50)
    
    # Change to project root
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    print(f"Working directory: {os.getcwd()}")
    
    # Clean old builds
    print("\n1. Cleaning old build files...")
    clean_build_dirs()
    
    # Build executable
    print("\n2. Creating executable...")
    if not create_executable():
        sys.exit(1)
    
    # Copy config files
    print("\n3. Copying configuration files...")
    copy_config_files()
    
    print("\n" + "=" * 50)
    print("Build complete!")
    print("=" * 50)
    print("\nTo run: dist\\SpatialTouch.exe")


if __name__ == '__main__':
    main()
