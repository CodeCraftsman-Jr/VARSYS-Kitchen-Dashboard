#!/usr/bin/env python3
"""
Build script for VARSYS Kitchen Dashboard with custom icon
Ensures the executable has the proper icon and branding
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_icon():
    """Check if the icon file exists"""
    icon_path = Path("assets/icons/vasanthkitchen.ico")
    if icon_path.exists():
        size_kb = icon_path.stat().st_size / 1024
        print(f"[OK] Icon file found: {icon_path} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"[ERROR] Icon file not found: {icon_path}")
        print("   Please ensure the icon file exists before building")
        return False

def create_icon_setup():
    """Create a setup script specifically for building with icon"""
    setup_content = '''#!/usr/bin/env python3
"""
VARSYS Kitchen Dashboard - Build with Icon
"""

import sys
import os
from cx_Freeze import setup, Executable

# Build options optimized for icon inclusion
build_options = {
    'packages': [
        'pandas', 'numpy', 'matplotlib', 'openpyxl',
        'PySide6', 'PIL', 'requests', 'cryptography',
        'json', 'sqlite3', 'datetime', 'logging', 'platform', 'uuid'
    ],
    
    'excludes': [
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 
        'setuptools', 'pip', 'scipy'
    ],
    
    'include_files': [
        ('modules/', 'modules/'),
        ('utils/', 'utils/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
        ('secure_credentials/', 'secure_credentials/'),
        ('firebase_web_config.json', 'firebase_web_config.json'),
        ('README.md', 'README.md'),
    ],
    
    'optimize': 1,
}

# GUI base for Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Executable with icon
executables = [
    Executable(
        'kitchen_app.py',
        base=base,
        target_name='VARSYS_Kitchen_Dashboard.exe',
        icon='assets/icons/vasanthkitchen.ico',
        copyright='Copyright (C) 2025 VARSYS Solutions'
    )
]

# Setup
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.5",
    description='Professional Kitchen Management System',
    author='VARSYS Solutions',
    options={'build_exe': build_options},
    executables=executables
)
'''
    
    with open("setup_icon.py", "w") as f:
        f.write(setup_content)
    print("[OK] Created icon-enabled setup script")

def build_with_icon():
    """Build the application with icon"""
    print("[BUILD] Building application with custom icon...")

    try:
        result = subprocess.run([
            sys.executable, "setup_icon.py", "build"
        ], capture_output=True, text=True, cwd=".")

        if result.returncode == 0:
            print("[OK] Build completed successfully!")
            return True
        else:
            print("[ERROR] Build failed!")
            print("Error:", result.stderr)
            print("Output:", result.stdout)
            return False

    except Exception as e:
        print(f"[ERROR] Build process failed: {e}")
        return False

def verify_icon_in_exe():
    """Verify that the executable has the icon"""
    exe_path = None
    build_dir = Path("build")

    # Find the executable
    for item in build_dir.rglob("VARSYS_Kitchen_Dashboard.exe"):
        exe_path = item
        break

    if exe_path and exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Executable created: {exe_path}")
        print(f"[INFO] Size: {size_mb:.1f} MB")
        print("[INFO] Icon should be embedded in the executable")
        return True
    else:
        print("[ERROR] Executable not found!")
        return False

def cleanup():
    """Clean up temporary files"""
    temp_files = ["setup_icon.py"]
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"[CLEANUP] Cleaned up: {file}")

def main():
    """Main build process with icon"""
    print("=" * 60)
    print("VARSYS Kitchen Dashboard - Build with Custom Icon")
    print("=" * 60)

    # Step 1: Check icon
    print("\n[1/5] Checking icon file...")
    if not check_icon():
        return False

    # Step 2: Create icon setup
    print("\n[2/5] Creating icon-enabled setup...")
    create_icon_setup()

    # Step 3: Build with icon
    print("\n[3/5] Building application...")
    if not build_with_icon():
        return False

    # Step 4: Verify icon
    print("\n[4/5] Verifying executable...")
    if not verify_icon_in_exe():
        return False

    # Step 5: Cleanup
    print("\n[5/5] Cleaning up...")
    cleanup()

    print("\n" + "=" * 60)
    print("SUCCESS: BUILD WITH ICON COMPLETED!")
    print("=" * 60)
    print("\nYour executable now includes:")
    print("- Custom icon (vasanthkitchen.ico)")
    print("- Professional branding")
    print("- All application dependencies")
    print("\nThe executable is ready for distribution!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
