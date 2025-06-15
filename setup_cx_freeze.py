#!/usr/bin/env python3
"""
cx_Freeze setup script for VARSYS Kitchen Dashboard
Creates a complete, standalone executable with all dependencies
"""

import sys
import os
from cx_Freeze import setup, Executable

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Simplified but comprehensive package list
build_options = {
    'packages': [
        # Essential packages for the application
        'pandas', 'numpy', 'matplotlib', 'openpyxl',
        'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
        'PySide6.QtCharts', 'PIL', 'requests', 'cryptography',
        'json', 'sqlite3', 'datetime', 'logging', 'platform', 'uuid'
    ],

    'excludes': [
        # Exclude unnecessary packages to reduce size
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 'setuptools', 'pip'
    ],

    'include_files': [
        # Include essential directories and files that exist
        ('modules/', 'modules/'),
        ('utils/', 'utils/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
        ('firebase_web_config.json', 'firebase_web_config.json'),
        ('README.md', 'README.md'),
        ('requirements.txt', 'requirements.txt'),
    ],

    # Optimize packaging
    'zip_include_packages': ['encodings', 'importlib'],
    'optimize': 1,
}

# GUI applications require a different base on Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Create the executable configuration
executables = [
    Executable(
        'kitchen_app.py',
        base=base,
        target_name='VARSYS_Kitchen_Dashboard.exe',
        copyright='Copyright (C) 2025 VARSYS Team'
    )
]

# Setup configuration
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.5",
    description='Professional Kitchen Management System',
    author='VARSYS Team',
    options={'build_exe': build_options},
    executables=executables
)
