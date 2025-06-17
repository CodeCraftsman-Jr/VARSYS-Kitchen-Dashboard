#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Firebase-Enabled cx_Freeze Build Script
Ensures ALL Firebase dependencies are properly included
"""

import sys
import os
import subprocess
from cx_Freeze import setup, Executable

# Version information
VERSION = "1.1.1"
COMPANY_NAME = "VARSYS Technologies"
PRODUCT_NAME = "VARSYS Kitchen Dashboard"

print(f"Building {PRODUCT_NAME} v{VERSION} with Complete Firebase Support")

def get_python_version():
    """Get Python version for build directory naming"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def check_and_install_firebase():
    """Ensure all Firebase packages are installed"""
    firebase_packages = [
        "firebase-admin",
        "pyrebase4", 
        "PyJWT",
        "cryptography",
        "google-auth",
        "google-cloud-core",
        "google-api-core",
        "grpcio",
        "protobuf"
    ]
    
    print("Checking Firebase dependencies...")
    for package in firebase_packages:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"   Ensured: {package}")
        except subprocess.CalledProcessError:
            print(f"   Warning: Could not install {package}")

def get_all_firebase_modules():
    """Get comprehensive list of Firebase-related modules"""
    firebase_modules = []
    
    # Try to detect installed Firebase modules
    try:
        import firebase_admin
        firebase_modules.extend([
            "firebase_admin",
            "firebase_admin.auth",
            "firebase_admin.firestore", 
            "firebase_admin.storage",
            "firebase_admin.credentials",
            "firebase_admin._auth_utils",
            "firebase_admin._http_client",
            "firebase_admin._token_gen",
            "firebase_admin._user_mgt",
            "firebase_admin._utils"
        ])
        print("   Including firebase_admin and submodules")
    except ImportError:
        print("   Warning: firebase_admin not available")
    
    try:
        import pyrebase
        firebase_modules.extend([
            "pyrebase",
            "pyrebase.pyrebase"
        ])
        print("   Including pyrebase")
    except ImportError:
        print("   Warning: pyrebase not available")
    
    try:
        import jwt
        firebase_modules.extend([
            "jwt",
            "jwt.algorithms",
            "jwt.api_jws",
            "jwt.api_jwt"
        ])
        print("   Including jwt")
    except ImportError:
        print("   Warning: jwt not available")
    
    # Google Cloud modules
    google_modules = [
        "google", "google.auth", "google.oauth2", "google.cloud",
        "google.api_core", "google.protobuf", "google.rpc",
        "google.type", "google.longrunning"
    ]
    
    for module in google_modules:
        try:
            __import__(module)
            firebase_modules.append(module)
        except ImportError:
            pass
    
    # gRPC and Protocol Buffers
    grpc_modules = [
        "grpc", "grpc._channel", "grpc._common", "grpc._compression",
        "grpc._interceptor", "grpc._plugin_wrapping", "grpc._server",
        "grpc._utilities", "grpc.aio", "grpc.experimental"
    ]
    
    for module in grpc_modules:
        try:
            __import__(module)
            firebase_modules.append(module)
        except ImportError:
            pass
    
    return firebase_modules

# Check and install Firebase dependencies
check_and_install_firebase()

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

# Core packages
core_packages = [
    "pandas", "numpy", "matplotlib", "PySide6", 
    "requests", "PIL", "openpyxl", "json", "csv", 
    "datetime", "os", "sys", "sqlite3", "logging",
    "pathlib", "shutil", "subprocess", "urllib",
    "cryptography", "certifi", "urllib3"
]

# Get Firebase modules
firebase_packages = get_all_firebase_modules()

# Combine all packages
all_packages = core_packages + firebase_packages

print(f"Total packages to include: {len(all_packages)}")
print(f"Firebase-related packages: {len(firebase_packages)}")

# Build options with comprehensive Firebase support
build_exe_options = {
    "packages": all_packages,
    "include_files": filtered_include_files,
    "optimize": 1,
    "build_exe": f"build/exe.win-amd64-{get_python_version()}",
    "excludes": [
        "tkinter", "unittest", "PyQt5", "PyQt6", "pytest", 
        "IPython", "jupyter", "notebook"
    ],
    # Force include critical Firebase modules
    "includes": firebase_packages,
    # Include all .py files in site-packages for Firebase
    "include_msvcrt": False,
    "zip_include_packages": [],
    "zip_exclude_packages": ["firebase_admin", "pyrebase", "google", "grpc"]
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

print("Firebase-Complete build configuration:")
print(f"   Target: VARSYS_Kitchen_Dashboard.exe")
print(f"   Output: build/exe.win-amd64-{get_python_version()}/")
print(f"   Firebase modules: {len(firebase_packages)}")
print(f"   Total files: {len(filtered_include_files)}")

# Setup configuration
setup(
    name=PRODUCT_NAME,
    version=VERSION,
    description="Kitchen Dashboard with Complete Firebase Support",
    author=COMPANY_NAME,
    options={"build_exe": build_exe_options},
    executables=executables
)

print("Firebase-complete build finished!")
print("This build should work on any Windows PC without Firebase installation requirements.")
