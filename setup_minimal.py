#!/usr/bin/env python3
"""
Minimal cx_Freeze setup for VARSYS Kitchen Dashboard
Just the basics to get it working
"""

import sys
import os
from cx_Freeze import setup, Executable

# Minimal build options
build_options = {
    'packages': [
        # Only the most essential packages
        'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui',
        'pandas', 'matplotlib', 'numpy'
    ],
    
    'excludes': [
        'tkinter', 'unittest', 'test', 'tests'
    ],
    
    'include_files': [
        # Only include files that definitely exist
        ('modules/', 'modules/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
    ],
    
    'optimize': 0,  # No optimization to avoid issues
}

# Check for optional files
if os.path.exists('utils/'):
    build_options['include_files'].append(('utils/', 'utils/'))

if os.path.exists('README.md'):
    build_options['include_files'].append(('README.md', 'README.md'))

# GUI base for Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Simple executable
executable = Executable(
    'kitchen_app.py',
    base=base,
    target_name='VARSYS_Kitchen_Dashboard.exe',
    icon='assets/icons/vasanthkitchen.ico' if os.path.exists('assets/icons/vasanthkitchen.ico') else None
)

# Minimal setup
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.6",
    options={'build_exe': build_options},
    executables=[executable]
)
