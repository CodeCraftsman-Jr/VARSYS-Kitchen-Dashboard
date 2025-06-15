#!/usr/bin/env python3
"""
Standalone cx_Freeze setup for VARSYS Kitchen Dashboard
Creates a single executable file with all dependencies included
"""

import sys
import os
from cx_Freeze import setup, Executable

# Standalone build options - everything in one file
build_options = {
    'packages': [
        # Essential packages only
        'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui',
        'pandas', 'matplotlib.pyplot', 'openpyxl', 'json', 'sqlite3',
        'datetime', 'logging', 'os', 'sys'
    ],
    
    'excludes': [
        # Exclude problematic and unnecessary packages
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 'setuptools', 'pip',
        'numpy.core._methods', 'numpy.lib.format', 'numpy.core.multiarray',
        'scipy', 'IPython', 'jupyter', 'notebook', 'sphinx', 'pytest'
    ],
    
    'include_files': [
        # Include essential data files
        ('modules/', 'modules/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
    ],
    
    'includes': [
        'matplotlib.backends.backend_qt5agg',
    ],
    
    # Simple settings that work with all cx_Freeze versions
    'optimize': 1,  # Basic optimization
}

# Check for optional files
optional_files = [
    ('utils/', 'utils/'),
    ('README.md', 'README.md'),
    ('secure_credentials/', 'secure_credentials/'),
    ('firebase_web_config.json', 'firebase_web_config.json'),
    ('__version__.py', '__version__.py'),
]

for src, dest in optional_files:
    if os.path.exists(src):
        build_options['include_files'].append((src, dest))

# GUI base for Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Standalone executable configuration
executable = Executable(
    'kitchen_app.py',
    base=base,
    target_name='VARSYS_Kitchen_Dashboard_Standalone.exe',
    icon='assets/icons/vasanthkitchen.ico' if os.path.exists('assets/icons/vasanthkitchen.ico') else None,
    copyright='Copyright (C) 2025 VARSYS Solutions'
)

# Setup for standalone build
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.6",
    description='Professional Kitchen Management System - Standalone',
    options={'build_exe': build_options},
    executables=[executable]
)
