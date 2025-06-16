"""
Fixed cx_Freeze setup for Kitchen Dashboard v1.1.1
Handles Python 3.12/3.13 compatibility issues and missing modules
"""

import sys
import os
from cx_Freeze import setup, Executable
import platform

# Application metadata
APP_NAME = "VARSYS Kitchen Dashboard"
APP_VERSION = "1.1.1"
APP_DESCRIPTION = "Professional Kitchen Management System"
APP_AUTHOR = "VARSYS"
APP_COPYRIGHT = "Copyright (c) 2025 VARSYS"

# Main script
MAIN_SCRIPT = "kitchen_app.py"

# Icon file
ICON_FILE = "assets/icons/vasanthkitchen.ico" if os.path.exists("assets/icons/vasanthkitchen.ico") else None

def get_safe_packages():
    """Get list of packages that are safe to include"""
    safe_packages = []
    
    # Core packages (always try to include)
    core_packages = [
        "pandas", "numpy", "matplotlib", "PySide6", 
        "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "matplotlib.backends.backend_qtagg"
    ]
    
    # Optional packages (include if available)
    optional_packages = [
        "openpyxl", "PIL", "requests", "urllib3", "certifi",
        "tqdm", "dateutil", "json", "datetime", "os", "sys",
        "pathlib", "collections", "itertools", "functools"
    ]
    
    # Test each package
    for package in core_packages + optional_packages:
        try:
            __import__(package)
            safe_packages.append(package)
            print(f"✓ Including {package}")
        except ImportError:
            print(f"- Skipping {package} (not available)")
    
    return safe_packages

def get_safe_files():
    """Get list of files that exist and can be included"""
    safe_files = []
    
    # Essential files
    essential_files = [
        ("data/", "data/"),
        ("modules/", "modules/"),
        ("utils/", "utils/"),
        ("__version__.py", "__version__.py"),
        ("version.py", "version.py")
    ]
    
    # Optional files
    optional_files = [
        ("assets/", "assets/"),
        ("logs/", "logs/"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE"),
        ("config.py", "config.py"),
        ("varsys_branding.py", "varsys_branding.py"),
        ("varsys_config.py", "varsys_config.py"),
        ("firebase_config.json", "firebase_config.json"),
        ("jwt_secret.key", "jwt_secret.key")
    ]
    
    # Check which files exist
    for src, dst in essential_files + optional_files:
        if os.path.exists(src):
            safe_files.append((src, dst))
            print(f"✓ Including {src}")
        else:
            print(f"- Skipping {src} (not found)")
    
    return safe_files

# Get safe packages and files
print("Scanning for available packages and files...")
safe_packages = get_safe_packages()
safe_files = get_safe_files()

# Build options for cx_Freeze with Python 3.12/3.13 fixes
build_exe_options = {
    # Include safe packages
    "packages": safe_packages,
    
    # Include safe files
    "include_files": safe_files,
    
    # Explicitly include standard library modules that might be missing
    "includes": [
        "html", "html.entities", "html.parser",
        "urllib", "urllib.parse", "urllib.request", "urllib.error",
        "http", "http.client", "http.server",
        "email", "email.mime", "email.mime.text",
        "json", "csv", "sqlite3", "datetime", "calendar",
        "collections", "collections.abc", "itertools", "functools",
        "pathlib", "tempfile", "shutil", "zipfile",
        "threading", "queue", "concurrent", "concurrent.futures"
    ],
    
    # Exclude problematic packages
    "excludes": [
        "tkinter", "unittest", "test", "distutils",
        "pydoc", "doctest", "pdb", "profile", "pstats", 
        "timeit", "trace", "turtle", "antigravity"
    ],
    
    # Build directory
    "build_exe": f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",
    
    # Optimization and compatibility settings
    "optimize": 1,  # Reduced optimization to avoid issues
    "include_msvcrt": True,  # Include Microsoft Visual C++ runtime
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
    
    # Python 3.12/3.13 specific fixes
    "replace_paths": [("*", "")],  # Remove absolute paths
    "include_in_shared_zip": False,  # Don't use shared zip for better compatibility
}

# MSI installer options
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-9012-123456789012}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\VARSYS\Kitchen Dashboard"
}

if ICON_FILE:
    bdist_msi_options["install_icon"] = ICON_FILE

# Create executable with error handling
base = None
if platform.system() == "Windows":
    base = "Win32GUI"  # Hide console window

# Define the executable
executable_options = {
    "script": MAIN_SCRIPT,
    "base": base,
    "target_name": "VARSYS_Kitchen_Dashboard.exe",
    "copyright": APP_COPYRIGHT,
    "trademarks": "VARSYS Kitchen Dashboard"
}

if ICON_FILE:
    executable_options["icon"] = ICON_FILE

executable = Executable(**executable_options)

# Setup configuration with error handling
try:
    setup(
        name=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        author=APP_AUTHOR,
        options={
            "build_exe": build_exe_options,
            "bdist_msi": bdist_msi_options
        },
        executables=[executable]
    )
    
    print(f"""
=== Fixed Build Configuration ===
Application: {APP_NAME} v{APP_VERSION}
Python Version: {sys.version}
Platform: {platform.system()} {platform.architecture()[0]}
Build Tool: cx_Freeze (Fixed)
Icon: {ICON_FILE if ICON_FILE else 'Default'}
Output: VARSYS_Kitchen_Dashboard.exe

Packages included: {len(safe_packages)}
Files included: {len(safe_files)}
Standard library modules: Explicitly included

Build directory: {build_exe_options['build_exe']}

This build configuration:
✓ Handles Python 3.12/3.13 compatibility
✓ Includes missing standard library modules
✓ Uses conservative optimization settings
✓ Includes Microsoft Visual C++ runtime
✓ Excludes problematic packages

To test the build:
cd {build_exe_options['build_exe']}
VARSYS_Kitchen_Dashboard.exe
""")

except Exception as e:
    print(f"""
❌ Build setup failed: {e}

Troubleshooting steps:
1. Update cx_Freeze: pip install --upgrade cx_Freeze
2. Check Python version: python --version
3. Try minimal build: python setup_cx_freeze_minimal.py build
4. Install missing dependencies: pip install -r requirements.txt

For Python 3.12/3.13 specific issues:
- Some standard library modules may need explicit inclusion
- Try using Python 3.11 if available
- Consider using PyInstaller as alternative
""")
    raise
