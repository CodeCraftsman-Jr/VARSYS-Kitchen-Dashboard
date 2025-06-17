#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple cx_Freeze Build Script for VARSYS Kitchen Dashboard
Minimal configuration for testing
"""

import sys
import os
from cx_Freeze import setup, Executable

# Version information
VERSION = "1.1.1"
COMPANY_NAME = "VARSYS Technologies"
PRODUCT_NAME = "VARSYS Kitchen Dashboard"

print(f"Building {PRODUCT_NAME} v{VERSION} (Simple Configuration)")

def get_python_version():
    """Get Python version for build directory naming"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

# Essential include files
include_files = [
    ("modules", "modules"),
    ("utils", "utils"),
    ("data", "data"),
    ("vasanthkitchen.ico", "vasanthkitchen.ico"),
    ("firebase_config.json", "firebase_config.json"),
    ("version.py", "version.py"),
    ("__version__.py", "__version__.py")
]

# Essential packages
packages = [
    "pandas", "numpy", "matplotlib", "PySide6", 
    "requests", "PIL", "openpyxl", "json", "csv", 
    "datetime", "os", "sys"
]

# Build options
build_exe_options = {
    "packages": packages,
    "include_files": include_files,
    "optimize": 1,
    "build_exe": f"build/exe.win-amd64-{get_python_version()}",
    "excludes": ["tkinter", "unittest", "email", "http.server"]
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

print("Simple build configuration:")
print(f"   Target: VARSYS_Kitchen_Dashboard.exe")
print(f"   Output: build/exe.win-amd64-{get_python_version()}/")
print(f"   Icon: {icon_path or 'None'}")
print(f"   Files to include: {len(include_files)}")
print(f"   Packages: {len(packages)}")

# Setup configuration
setup(
    name=PRODUCT_NAME,
    version=VERSION,
    description="Kitchen Dashboard Application",
    author=COMPANY_NAME,
    options={"build_exe": build_exe_options},
    executables=executables
)

print("Simple build completed!")
