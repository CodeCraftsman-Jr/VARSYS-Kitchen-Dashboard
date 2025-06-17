#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final cx_Freeze Build Script with Firebase Fallback Support
Includes comprehensive Firebase support with graceful fallback handling
"""

import sys
import os
import subprocess
from cx_Freeze import setup, Executable

# Version information
VERSION = "1.1.1"
COMPANY_NAME = "VARSYS Technologies"
PRODUCT_NAME = "VARSYS Kitchen Dashboard"

print(f"Building {PRODUCT_NAME} v{VERSION} (Final Build with Firebase Fallback)")

def get_python_version():
    """Get Python version for build directory naming"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def ensure_firebase_packages():
    """Ensure Firebase packages are installed"""
    firebase_packages = [
        "firebase-admin",
        "pyrebase4", 
        "PyJWT",
        "cryptography>=3.0.0",
        "google-auth",
        "google-cloud-firestore",
        "grpcio",
        "protobuf"
    ]
    
    print("Ensuring Firebase packages are installed...")
    for package in firebase_packages:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   OK: {package}")
            else:
                print(f"   Warning: {package} installation had issues")
        except subprocess.TimeoutExpired:
            print(f"   Timeout: {package} installation timed out")
        except Exception as e:
            print(f"   Error: {package} - {e}")

# Ensure Firebase packages
ensure_firebase_packages()

# Essential include files
include_files = [
    ("modules", "modules"),
    ("utils", "utils"),
    ("data", "data"),
    ("tests", "tests"),
    ("assets", "assets"),
    ("secure_credentials", "secure_credentials"),
    ("firebase_fallback_handler.py", "firebase_fallback_handler.py"),
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

# Filter existing files
filtered_include_files = []
for src, dst in include_files:
    if os.path.exists(src):
        filtered_include_files.append((src, dst))
        print(f"   Including: {src}")
    else:
        print(f"   Warning: {src} not found")

# Core packages
core_packages = [
    "pandas", "numpy", "matplotlib", "PySide6", 
    "requests", "PIL", "openpyxl", "json", "csv", 
    "datetime", "os", "sys", "sqlite3", "logging",
    "pathlib", "shutil", "subprocess", "urllib",
    "cryptography", "certifi", "urllib3", "tqdm"
]

# Firebase packages - try to include what's available
firebase_packages = []
firebase_modules_to_try = [
    "firebase_admin",
    "pyrebase", 
    "jwt",
    "google.auth",
    "google.cloud",
    "google.api_core",
    "grpc",
    "proto"
]

print("Checking Firebase modules...")
for module in firebase_modules_to_try:
    try:
        __import__(module)
        firebase_packages.append(module)
        print(f"   Found: {module}")
    except ImportError:
        print(f"   Missing: {module}")

# Combine packages
all_packages = core_packages + firebase_packages

print(f"Total packages: {len(all_packages)}")
print(f"Firebase packages: {len(firebase_packages)}")

# Build options
build_exe_options = {
    "packages": all_packages,
    "include_files": filtered_include_files,
    "optimize": 1,
    "build_exe": f"build/exe.win-amd64-{get_python_version()}",
    "excludes": [
        "tkinter", "unittest", "PyQt5", "PyQt6", "pytest", 
        "IPython", "jupyter", "notebook", "email", "http.server"
    ],
    # Include Firebase modules if available
    "includes": firebase_packages if firebase_packages else [],
    # Don't zip Firebase packages to ensure they're accessible
    "zip_exclude_packages": firebase_packages if firebase_packages else []
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

print("Final build configuration:")
print(f"   Target: VARSYS_Kitchen_Dashboard.exe")
print(f"   Output: build/exe.win-amd64-{get_python_version()}/")
print(f"   Icon: {icon_path or 'None'}")
print(f"   Files: {len(filtered_include_files)}")
print(f"   Core packages: {len(core_packages)}")
print(f"   Firebase packages: {len(firebase_packages)}")
print(f"   Fallback handler: Included")

# Setup configuration
setup(
    name=PRODUCT_NAME,
    version=VERSION,
    description="Kitchen Dashboard with Firebase Fallback Support",
    author=COMPANY_NAME,
    options={"build_exe": build_exe_options},
    executables=executables
)

print("Final build completed!")
print("This build includes Firebase fallback handling for better compatibility.")
print(f"Executable: build/exe.win-amd64-{get_python_version()}/VARSYS_Kitchen_Dashboard.exe")
