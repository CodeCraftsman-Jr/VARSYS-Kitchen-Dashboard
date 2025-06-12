#!/usr/bin/env python3
"""
cx_Freeze setup script for VARSYS Kitchen Dashboard
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': [
        'pandas', 'numpy', 'matplotlib', 'openpyxl', 'PIL',
        'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'
    ],
    'excludes': [
        'tkinter', 'unittest', 'email', 'http', 'urllib', 'xml',
        'multiprocessing', 'concurrent', 'asyncio', 'test'
    ],
    'include_files': [],
    'zip_include_packages': ['encodings', 'importlib'],
}

# GUI applications require a different base on Windows (the default is for a console application).
base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable(
        'kitchen_app.py',
        base=base,
        target_name='VARSYS_Kitchen_Dashboard.exe',
        icon='assets/icons/app_icon.ico' if 'assets/icons/app_icon.ico' else None
    )
]

setup(
    name='VARSYS Kitchen Dashboard',
    version='1.0.0',
    description='Professional Kitchen Management Dashboard',
    author='VARSYS',
    options={'build_exe': build_options},
    executables=executables
)
