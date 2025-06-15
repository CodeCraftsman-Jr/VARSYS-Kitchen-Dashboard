#!/usr/bin/env python3
"""
Working cx_Freeze setup for VARSYS Kitchen Dashboard
Avoids numpy import issues by using specific exclusions and includes
"""

import sys
import os
from cx_Freeze import setup, Executable

# Working build options that avoid numpy issues
build_options = {
    'packages': [
        # Core packages only - avoid numpy for now
        'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui',
        'pandas', 'matplotlib.pyplot', 'openpyxl'
    ],
    
    'excludes': [
        # Exclude problematic packages
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 'setuptools', 'pip',
        'numpy.core._methods', 'numpy.lib.format', 'numpy.core.multiarray',
        'scipy', 'IPython', 'jupyter', 'notebook'
    ],
    
    'include_files': [
        # Only essential files
        ('modules/', 'modules/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
    ],
    
    # Add specific includes to handle dependencies
    'includes': [
        'matplotlib.backends.backend_qt5agg',
    ],
    
    'optimize': 0,  # No optimization to avoid issues
    'silent': True,  # Reduce output
}

# Check for optional files
optional_files = [
    ('utils/', 'utils/'),
    ('README.md', 'README.md'),
    ('secure_credentials/', 'secure_credentials/'),
]

for src, dest in optional_files:
    if os.path.exists(src):
        build_options['include_files'].append((src, dest))

# GUI base for Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Simple executable
executable = Executable(
    'kitchen_app.py',
    base=base,
    target_name='VARSYS_Kitchen_Dashboard.exe',
    icon='assets/icons/vasanthkitchen.ico' if os.path.exists('assets/icons/vasanthkitchen.ico') else None
)

# Setup with error handling
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.6",
    options={'build_exe': build_options},
    executables=[executable]
)
