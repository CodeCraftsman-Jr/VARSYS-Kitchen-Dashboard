"""
Professional cx_Freeze build setup for Kitchen Dashboard
Compatible with Python 3.12 and 3.13
"""

import sys
import os
from cx_Freeze import setup, Executable
import platform

# Application metadata
APP_NAME = "VARSYS Kitchen Dashboard"
APP_VERSION = "1.1.1"
APP_DESCRIPTION = "Professional Kitchen Management System with Firebase Authentication & Cloud Sync"
APP_AUTHOR = "VARSYS"
APP_COPYRIGHT = "Copyright (c) 2025 VARSYS"

# Main script
MAIN_SCRIPT = "kitchen_app.py"

# Icon file
ICON_FILE = "assets/icons/vasanthkitchen.ico"

# Build options for cx_Freeze
build_exe_options = {
    # Include all necessary packages (Firebase enabled for v1.1.1)
    "packages": [
        "pandas", "numpy", "matplotlib", "seaborn", "openpyxl",
        "PySide6", "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "matplotlib.backends.backend_qtagg",
        # Firebase packages (enabled)
        "firebase_admin", "pyrebase", "google.cloud.firestore", "google.auth",
        "requests", "urllib3", "certifi",
        "PIL", "tqdm", "dateutil", "sklearn",
        "jwt", "cryptography", "loguru", "json5", "dotenv"
    ],

    # Include all files from these directories
    "include_files": [
        ("data/", "data/"),
        ("modules/", "modules/"),
        ("utils/", "utils/"),
        ("assets/", "assets/"),
        ("secure_credentials/", "secure_credentials/"),
        ("logs/", "logs/"),
        ("firebase_config.json", "firebase_config.json"),
        ("firebase_web_config.json", "firebase_web_config.json"),
        ("jwt_secret.key", "jwt_secret.key"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE"),
        ("__version__.py", "__version__.py"),
        ("version.py", "version.py"),
        ("config.py", "config.py"),
        ("varsys_config.py", "varsys_config.py"),
        ("varsys_branding.py", "varsys_branding.py")
    ],

    # Exclude unnecessary packages to reduce size
    "excludes": [
        "tkinter", "unittest", "test", "distutils", "setuptools",
        "email", "html", "http", "urllib", "xml", "xmlrpc",
        "pydoc", "doctest", "argparse", "difflib", "inspect",
        "pdb", "profile", "pstats", "timeit", "trace"
    ],

    # Include DLLs and dependencies
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],

    # Build directory
    "build_exe": "build/exe.win-amd64-3.12" if sys.version_info[:2] == (3, 12) else "build/exe.win-amd64-3.13",

    # Optimize for size and performance
    "optimize": 2
}

# MSI installer options
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-9012-123456789012}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\VARSYS\Kitchen Dashboard",
    "install_icon": ICON_FILE
}

# Create executable
base = None
if platform.system() == "Windows":
    base = "Win32GUI"  # Hide console window

# Define the executable
executable = Executable(
    script=MAIN_SCRIPT,
    base=base,
    icon=ICON_FILE,
    target_name="VARSYS_Kitchen_Dashboard.exe",
    copyright=APP_COPYRIGHT,
    trademarks="VARSYS Kitchen Dashboard"
)

# Setup configuration
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[executable]
)

print(f"""
=== Build Configuration ===
Application: {APP_NAME} v{APP_VERSION}
Python Version: {sys.version}
Platform: {platform.system()} {platform.architecture()[0]}
Build Tool: cx_Freeze
Icon: {ICON_FILE}
Output: VARSYS_Kitchen_Dashboard.exe

To build:
1. Install dependencies: py -3.12 -m pip install -r requirements.txt
2. Build executable: py -3.12 setup_cx_freeze.py build
3. Create installer: py -3.12 setup_cx_freeze.py bdist_msi

For Python 3.13, replace 'py -3.12' with 'python' (if 3.13 is default)
""")