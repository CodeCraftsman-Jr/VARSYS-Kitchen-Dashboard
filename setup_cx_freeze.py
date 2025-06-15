#!/usr/bin/env python3
"""
Enhanced cx_Freeze setup script for VARSYS Kitchen Dashboard
Creates a professional, standalone executable with all dependencies
Includes system tray integration and auto-startup capabilities
"""

import sys
import os
from cx_Freeze import setup, Executable

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Enhanced package list with system tray and Windows integration
build_options = {
    'packages': [
        # Core Python packages
        'os', 'sys', 'json', 'sqlite3', 'datetime', 'logging', 'platform', 'uuid',
        'pathlib', 'tempfile', 'shutil', 'subprocess', 'threading', 'time',
        'ctypes', 'ctypes.wintypes', 'atexit', 'signal', 'winreg',

        # Scientific computing packages
        'pandas', 'numpy', 'matplotlib',

        # GUI packages with system tray support
        'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',

        # Image and file handling
        'PIL', 'openpyxl',

        # Network and security
        'requests', 'urllib3', 'ssl', 'certifi', 'cryptography',

        # Additional packages
        'tqdm', 'dateutil'
    ],

    'excludes': [
        # Exclude unnecessary packages to reduce size
        'tkinter', 'unittest', 'test', 'tests', 'distutils', 'setuptools', 'pip',
        'scipy', 'IPython', 'jupyter', 'notebook', 'sphinx', 'pytest',
        'numpy.core._methods', 'numpy.lib.format', 'pandas._libs.tslibs.base'
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
        ('LICENSE', 'LICENSE'),
        ('version.py', 'version.py'),
        ('__version__.py', '__version__.py'),
        ('config.py', 'config.py'),
        ('manifest.json', 'manifest.json'),
    ],

    # Include additional modules that might be missed
    'includes': [
        'matplotlib.backends.backend_qtagg',
    ],

    # Optimize packaging
    'zip_include_packages': ['encodings', 'importlib', 'collections'],
    'optimize': 2,
    'build_exe': 'build/exe',
}

# GUI applications require a different base on Windows
base = 'Win32GUI' if sys.platform == 'win32' else None

# Create the main executable configuration
main_executable = Executable(
    'kitchen_app.py',
    base=base,
    target_name='VARSYS_Kitchen_Dashboard.exe',
    icon='assets/icons/vasanthkitchen.ico',
    copyright='Copyright (C) 2025 VARSYS Solutions',
    shortcut_name='VARSYS Kitchen Dashboard',
    shortcut_dir='DesktopFolder',
)

executables = [main_executable]

# Enhanced setup configuration
setup(
    name='VARSYS Kitchen Dashboard',
    version="1.0.6",
    description='Professional Kitchen Management System with Cloud Sync',
    long_description='A comprehensive kitchen management solution with Firebase integration, subscription-based access, and professional Windows integration.',
    author='VARSYS Solutions',
    author_email='support@varsys.com',
    url='https://github.com/varsys/kitchen-dashboard',
    license='Commercial',
    options={'build_exe': build_options},
    executables=executables
)
