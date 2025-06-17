#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working cx_Freeze Build Script for VARSYS Kitchen Dashboard
Simplified configuration that works reliably
"""

import sys
import os
from cx_Freeze import setup, Executable

# Version information
VERSION = "1.1.1"
COMPANY_NAME = "VARSYS Technologies"
PRODUCT_NAME = "VARSYS Kitchen Dashboard"

print(f"Building {PRODUCT_NAME} v{VERSION} (Working Configuration)")

def get_python_version():
    """Get Python version for build directory naming"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

# Essential include files
include_files = [
    ("modules", "modules"),
    ("utils", "utils"),
    ("data", "data"),
    ("tests", "tests"),
    ("assets", "assets"),
    ("secure_credentials", "secure_credentials"),
    ("vasanthkitchen.ico", "vasanthkitchen.ico"),
    ("firebase_config.json", "firebase_config.json"),
    ("firebase_credentials.json", "firebase_credentials.json"),
    ("firebase_web_config.json", "firebase_web_config.json"),
    ("jwt_secret.key", "jwt_secret.key"),
    ("version.py", "version.py"),
    ("__version__.py", "__version__.py"),
    ("manifest.json", "manifest.json"),
    ("config.py", "config.py"),
    ("varsys_config.py", "varsys_config.py"),
    ("enterprise.db", "enterprise.db"),
    ("offline_data.db", "offline_data.db"),
    ("update_manager.py", "update_manager.py"),
    ("updater.py", "updater.py"),
    ("enhanced_updater.py", "enhanced_updater.py"),
    ("update_checker.py", "update_checker.py"),
    ("firebase_installer.py", "firebase_installer.py"),
    ("firebase_protection.py", "firebase_protection.py"),
    ("protected_firebase.py", "protected_firebase.py"),
    ("create_user.py", "create_user.py"),
    ("reset_password.py", "reset_password.py"),
    ("credential_manager.py", "credential_manager.py"),
    ("license_manager.py", "license_manager.py"),
    ("license_dialog.py", "license_dialog.py"),
    ("auto_cleanup.py", "auto_cleanup.py"),
    ("system_tray_service.py", "system_tray_service.py"),
    ("varsys_branding.py", "varsys_branding.py"),
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE"),
    ("requirements.txt", "requirements.txt")
]

# Filter to only include files that exist
filtered_include_files = []
for src, dst in include_files:
    if os.path.exists(src):
        filtered_include_files.append((src, dst))
        print(f"   Including: {src}")
    else:
        print(f"   Warning: {src} not found")

# Essential packages - only include what we know works
packages = [
    "pandas", "numpy", "matplotlib", "PySide6", 
    "requests", "PIL", "openpyxl", "json", "csv", 
    "datetime", "os", "sys", "sqlite3", "logging",
    "pathlib", "shutil", "subprocess", "urllib",
    "cryptography", "certifi"
]

# Try to include Firebase packages if available - ENHANCED FOR HTTPLIB2 ISSUE
firebase_packages = []

# Basic Firebase packages that we know work
try:
    import pyrebase
    firebase_packages.extend(["pyrebase"])
    print("   Including: pyrebase")
except ImportError:
    print("   Warning: pyrebase not available")

try:
    import jwt
    firebase_packages.extend(["jwt"])
    print("   Including: jwt")
except ImportError:
    print("   Warning: jwt not available")

# Fix httplib2 circular import issue - CRITICAL FOR PYREBASE
try:
    import httplib2
    firebase_packages.extend(["httplib2", "httplib2.socks"])
    print("   Including: httplib2 with socks support")
except ImportError:
    print("   Warning: httplib2 not available")

# Include socks module separately to fix circular import
try:
    import socks
    firebase_packages.extend(["socks"])
    print("   Including: socks module")
except ImportError:
    print("   Warning: socks module not available")

# Include additional networking modules for Firebase
try:
    import urllib3.contrib.socks
    firebase_packages.extend(["urllib3.contrib.socks"])
    print("   Including: urllib3.contrib.socks")
except ImportError:
    print("   Warning: urllib3.contrib.socks not available")

# Add Firebase packages to main packages list
packages.extend(firebase_packages)
print(f"   Total Firebase packages added: {len(firebase_packages)}")
print("   Note: Enhanced Firebase support with httplib2 fix")

# Build options with enhanced Firebase support
build_exe_options = {
    "packages": packages,
    "include_files": filtered_include_files,
    "includes": [
        # Firebase and networking - CRITICAL FIXES FOR HTTPLIB2 ISSUE
        "pyrebase", "jwt", "httplib2", "socks", "urllib3.contrib.socks",
        "requests", "certifi", "cryptography", "httplib2.socks",
        # Core modules
        "json", "csv", "sqlite3", "datetime", "pathlib", "shutil",
        "subprocess", "urllib", "collections", "threading", "multiprocessing"
    ],
    "optimize": 1,  # Reduced optimization to avoid issues
    "build_exe": f"build/exe.win-amd64-{get_python_version()}",
    "excludes": [
        "tkinter", "unittest", "email", "http.server",
        "PyQt5", "PyQt6", "pytest", "IPython", "jupyter"
    ]
}

# Executable configuration
icon_path = "vasanthkitchen.ico" if os.path.exists("vasanthkitchen.ico") else None

executables = [
    Executable(
        script="kitchen_app.py",
        base="Win32GUI",
        target_name="VARSYS_Kitchen_Dashboard.exe",
        icon=icon_path
    )
]

print("Working build configuration:")
print(f"   Target: VARSYS_Kitchen_Dashboard.exe")
print(f"   Output: build/exe.win-amd64-{get_python_version()}/")
print(f"   Icon: {icon_path or 'None'}")
print(f"   Files to include: {len(filtered_include_files)}")
print(f"   Packages: {len(packages)}")
print(f"   Optimization: Level 1")

# Setup configuration
setup(
    name=PRODUCT_NAME,
    version=VERSION,
    description="Kitchen Dashboard Application",
    author=COMPANY_NAME,
    options={"build_exe": build_exe_options},
    executables=executables
)

print("Working build completed!")
print(f"Executable should be in: build/exe.win-amd64-{get_python_version()}/VARSYS_Kitchen_Dashboard.exe")
