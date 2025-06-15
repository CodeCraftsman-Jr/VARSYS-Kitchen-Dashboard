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

# Comprehensive package list with proper numpy handling
build_options = {
    'packages': [
        # Core Python packages
        'os', 'sys', 'json', 'sqlite3', 'datetime', 'logging', 'platform', 'uuid',
        'pathlib', 'tempfile', 'shutil', 'subprocess', 'threading', 'time',

        # Scientific computing packages
        'numpy', 'numpy.core', 'numpy.lib', 'numpy.random',
        'pandas', 'pandas.core', 'pandas.io',
        'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends',
        'matplotlib.backends.backend_qt5agg',

        # GUI packages
        'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
        'PySide6.QtCharts', 'PySide6.QtNetwork', 'PySide6.QtSvg',

        # Image and file handling
        'PIL', 'PIL.Image', 'openpyxl', 'openpyxl.workbook',

        # Network and security
        'requests', 'urllib3', 'ssl', 'certifi', 'cryptography',

        # Additional packages
        'seaborn', 'tqdm', 'dateutil'
    ],

    'excludes': [
        # Exclude unnecessary packages to reduce size
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 'setuptools', 'pip',
        'scipy', 'IPython', 'jupyter', 'notebook'
    ],

    'include_files': [
        # Include essential directories and files that exist
        ('modules/', 'modules/'),
        ('utils/', 'utils/'),
        ('data/', 'data/'),
        ('assets/', 'assets/'),
        ('secure_credentials/', 'secure_credentials/'),
        ('firebase_web_config.json', 'firebase_web_config.json'),
        ('README.md', 'README.md'),
        ('requirements.txt', 'requirements.txt'),
    ],

    # Include additional modules that might be missed
    'includes': [
        'numpy.core._methods',
        'numpy.lib.format',
        'pandas._libs.tslibs.base',
        'matplotlib.backends.backend_qt5agg',
    ],

    # Optimize packaging
    'zip_include_packages': ['encodings', 'importlib', 'collections'],
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
        icon='assets/icons/vasanthkitchen.ico',
        copyright='Copyright (C) 2025 VARSYS Solutions'
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
