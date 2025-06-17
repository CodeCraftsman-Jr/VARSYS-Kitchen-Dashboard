#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VARSYS Kitchen Dashboard - cx_Freeze Build Script
Professional Windows executable builder with comprehensive file inclusion

This script builds the Kitchen Dashboard application into a Windows executable
using cx_Freeze with all required modules, data files, and supporting files.

Features:
- Complete module inclusion (modules/, utils/, tests/)
- All data files and configurations
- Firebase integration files
- Auto-update system files
- Test utilities and scripts
- Professional executable with icon
- Comprehensive error handling
"""

import sys
import os
from pathlib import Path
from cx_Freeze import setup, Executable
import platform

# Version information
VERSION = "1.1.1"
COMPANY_NAME = "VARSYS Technologies"
PRODUCT_NAME = "VARSYS Kitchen Dashboard"
DESCRIPTION = "Professional Kitchen Management Dashboard with Firebase Cloud Sync"

print(f"Building {PRODUCT_NAME} v{VERSION}")
print(f"Using cx_Freeze on {platform.system()} {platform.release()}")

# Base directory
BASE_DIR = Path(__file__).parent.absolute()
print(f"Base directory: {BASE_DIR}")

# Ensure we're in the correct directory
os.chdir(BASE_DIR)

def get_python_version():
    """Get Python version for build directory naming"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def collect_all_files():
    """Collect all files that need to be included in the build"""
    include_files = []
    
    # Core directories to include completely
    core_directories = [
        "modules",
        "utils", 
        "tests",
        "data",
        "assets",
        "secure_credentials",
        "release_tools",
        "docs",
        "logs"
    ]
    
    print("Collecting core directories...")
    for directory in core_directories:
        if os.path.exists(directory):
            include_files.append((directory, directory))
            print(f"   Found: {directory}/")
        else:
            print(f"   Warning: {directory}/ not found, creating empty directory")
            os.makedirs(directory, exist_ok=True)
            include_files.append((directory, directory))
    
    # Individual files to include
    individual_files = [
        # Configuration files
        "firebase_config.json",
        "firebase_credentials.json",
        "firebase_web_config.json",
        "jwt_secret.key",
        "manifest.json",
        "config.py",
        "varsys_config.py",
        
        # Database files
        "enterprise.db",
        "offline_data.db",
        
        # Version and update files
        "__version__.py",
        "version.py",
        "version_info.txt",
        "last_update_check.json",
        
        # Update system
        "update_manager.py",
        "updater.py", 
        "enhanced_updater.py",
        "update_checker.py",
        "update_firebase_config.py",
        
        # Firebase and authentication
        "firebase_installer.py",
        "firebase_protection.py",
        "protected_firebase.py",
        "create_user.py",
        "reset_password.py",
        "credential_manager.py",
        "license_manager.py",
        "license_dialog.py",
        
        # Utility scripts
        "auto_cleanup.py",
        "cleanup_sample_data.py",
        "quick_cleanup.py",
        "reset_data.py",
        "run_app_safe.py",
        "system_tray_service.py",
        "map_recipes_to_appliances.py",
        "check_firebase_files.py",
        "verify_security.py",
        
        # Test files
        "test_app_firebase_status.py",
        "test_auto_update.py", 
        "test_daily_sync_fix.py",
        "test_firebase_integration.py",
        "test_firebase_simple.py",
        "test_online_only_enforcement.py",
        "test_subscription_auth.py",
        "safe_comprehensive_test.py",
        
        # Release and build files
        "release.py",
        
        # Batch and shell scripts
        "run_tests.bat",
        "run_tests.sh",
        "create_github_release.bat",
        
        # Branding and styling
        "varsys_branding.py",
        
        # Icon file
        "vasanthkitchen.ico",
        
        # Documentation
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        
        # Requirements files
        "requirements.txt",
        "requirements_build.txt"
    ]
    
    print("Collecting individual files...")
    for file_path in individual_files:
        if os.path.exists(file_path):
            include_files.append((file_path, file_path))
            print(f"   Found: {file_path}")
        else:
            print(f"   Warning: {file_path} not found")
    
    # Special handling for release directory
    if os.path.exists("release"):
        include_files.append(("release", "release"))
        print("   Found: release/")

    print(f"Total files/directories to include: {len(include_files)}")
    return include_files

def get_packages():
    """Get list of packages to include"""
    packages = [
        # Core Python packages
        "os", "sys", "json", "csv", "sqlite3", "datetime", "time", "threading",
        "logging", "traceback", "pathlib", "shutil", "subprocess", "urllib",

        # Data handling
        "pandas", "numpy", "openpyxl", "xlsxwriter",

        # GUI framework
        "PySide6", "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",

        # Plotting and visualization
        "matplotlib", "matplotlib.backends", "matplotlib.backends.backend_qtagg",
        "seaborn",

        # Firebase and authentication - COMPLETE INCLUSION
        "firebase_admin", "firebase_admin.auth", "firebase_admin.firestore",
        "firebase_admin.storage", "firebase_admin.credentials",
        "pyrebase",
        "jwt", "python_jwt",
        "cryptography", "cryptography.fernet", "cryptography.hazmat",
        "google", "google.cloud", "google.auth", "google.oauth2",
        "grpc", "proto",

        # HTTP and networking
        "requests", "urllib3", "certifi", "httplib2", "httpx",

        # Utilities
        "tqdm", "python_dateutil", "dotenv", "loguru", "json5",

        # Machine learning (optional)
        "sklearn", "scipy",

        # Image processing
        "PIL", "Pillow",

        # Windows specific
        "win32api", "win32con", "win32gui", "pywintypes"
    ]

    print(f"Including {len(packages)} packages")
    return packages

def get_excludes():
    """Get list of modules to exclude from build"""
    excludes = [
        # Development tools
        "pytest", "unittest", "doctest",
        
        # Unused GUI frameworks
        "tkinter", "PyQt5", "PyQt6",
        
        # Development and testing
        "IPython", "jupyter", "notebook",
        
        # Unused packages
        "email", "http.server", "xmlrpc",
        
        # Large unused packages
        "scipy.spatial.distance._hausdorff",
        
        # Matplotlib backends we don't need
        "matplotlib.backends.backend_gtk3agg",
        "matplotlib.backends.backend_gtk4agg", 
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends.backend_webagg"
    ]
    
    print(f"Excluding {len(excludes)} unnecessary modules")
    return excludes

# Build options
build_exe_options = {
    "packages": get_packages(),
    "excludes": get_excludes(),
    "include_files": collect_all_files(),
    "optimize": 2,
    "build_exe": f"build/exe.win-amd64-{get_python_version()}",
    "silent": False,
    # Force include Firebase modules
    "includes": [
        "firebase_admin", "pyrebase", "jwt",
        "cryptography", "google.auth", "google.cloud", "grpc"
    ]
}

# Executable configuration
icon_path = "vasanthkitchen.ico" if os.path.exists("vasanthkitchen.ico") else None
if icon_path:
    print(f"Using icon: {icon_path}")
else:
    print("Warning: No icon file found")

executables = [
    Executable(
        script="kitchen_app.py",
        base="Win32GUI",  # Windows GUI application (no console)
        target_name="VARSYS_Kitchen_Dashboard.exe",
        icon=icon_path,
        copyright=f"Copyright (C) 2024 {COMPANY_NAME}",
        trademarks=f"{PRODUCT_NAME} is a trademark of {COMPANY_NAME}"
    )
]

print("Build configuration:")
print(f"   Target: VARSYS_Kitchen_Dashboard.exe")
print(f"   Output: build/exe.win-amd64-{get_python_version()}/")
print(f"   Base: Win32GUI (no console window)")
print(f"   Icon: {icon_path or 'None'}")
print(f"   Optimization: Level 2")

# Setup configuration
setup(
    name=PRODUCT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=COMPANY_NAME,
    options={"build_exe": build_exe_options},
    executables=executables
)

print("Build script completed!")
print(f"Executable should be in: build/exe.win-amd64-{get_python_version()}/VARSYS_Kitchen_Dashboard.exe")
print("To create installer, run the Inno Setup script: VARSYS_Kitchen_Dashboard_Setup.iss")
