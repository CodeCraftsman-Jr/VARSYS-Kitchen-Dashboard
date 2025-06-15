#!/usr/bin/env python3
"""
Simple cx_Freeze setup for VARSYS Kitchen Dashboard
Minimal configuration to get a working executable
"""

import sys
import os
from cx_Freeze import setup, Executable

# Simple build options that should work
build_options = {
    'packages': [
        # Essential packages only
        'pandas', 'numpy', 'matplotlib', 'PySide6', 'openpyxl', 
        'PIL', 'requests', 'json', 'sqlite3', 'datetime', 'logging'
    ],
    
    'excludes': [
        # Exclude problematic packages
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 'setuptools', 'pip'
    ],
    
    'include_files': [
        # Include only essential files that exist
        ('modules/', 'modules/'),
        ('utils/', 'utils/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
        ('README.md', 'README.md'),
    ],
    
    # Simple optimization
    'optimize': 1,
}

# Check if files exist before including them
optional_files = [
    ('secure_credentials/', 'secure_credentials/'),
    ('firebase_web_config.json', 'firebase_web_config.json'),
    ('requirements.txt', 'requirements.txt'),
    ('LICENSE', 'LICENSE'),
    ('__version__.py', '__version__.py'),
    ('config.py', 'config.py'),
]

for src, dest in optional_files:
    if os.path.exists(src):
        build_options['include_files'].append((src, dest))

# GUI base for Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Simple executable configuration
executable = Executable(
    'kitchen_app.py',
    base=base,
    target_name='VARSYS_Kitchen_Dashboard.exe',
    icon='assets/icons/vasanthkitchen.ico' if os.path.exists('assets/icons/vasanthkitchen.ico') else None,
    copyright='Copyright (C) 2025 VARSYS Solutions'
)

# Simple setup
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.6",
    description='Professional Kitchen Management System',
    author='VARSYS Solutions',
    options={'build_exe': build_options},
    executables=[executable]
)
