"""
Minimal cx_Freeze setup for Kitchen Dashboard v1.1.1
Excludes problematic Firebase dependencies for reliable building
"""

import sys
import os
from cx_Freeze import setup, Executable
import platform

# Application metadata
APP_NAME = "VARSYS Kitchen Dashboard"
APP_VERSION = "1.1.1"
APP_DESCRIPTION = "Professional Kitchen Management System"
APP_AUTHOR = "VARSYS"
APP_COPYRIGHT = "Copyright (c) 2025 VARSYS"

# Main script
MAIN_SCRIPT = "kitchen_app.py"

# Icon file
ICON_FILE = "assets/icons/vasanthkitchen.ico" if os.path.exists("assets/icons/vasanthkitchen.ico") else None

# Check which packages are actually available
def check_package_availability():
    """Check which packages are available for inclusion"""
    available_packages = []
    required_packages = [
        "pandas", "numpy", "matplotlib", "PySide6", "openpyxl"
    ]
    
    optional_packages = [
        "seaborn", "PIL", "requests", "urllib3", "certifi",
        "tqdm", "dateutil", "sklearn", "jwt", "cryptography"
    ]
    
    firebase_packages = [
        "firebase_admin", "pyrebase4"
    ]
    
    # Check required packages
    for package in required_packages:
        try:
            __import__(package)
            available_packages.append(package)
            print(f"✓ {package} available")
        except ImportError:
            print(f"✗ {package} missing (REQUIRED)")
    
    # Check optional packages
    for package in optional_packages:
        try:
            __import__(package)
            available_packages.append(package)
            print(f"✓ {package} available")
        except ImportError:
            print(f"- {package} missing (optional)")
    
    # Check Firebase packages
    firebase_available = True
    for package in firebase_packages:
        try:
            __import__(package)
            available_packages.append(package)
            print(f"✓ {package} available")
        except ImportError:
            print(f"- {package} missing (Firebase disabled)")
            firebase_available = False
    
    return available_packages, firebase_available

print("Checking package availability...")
available_packages, firebase_available = check_package_availability()

# Build options for cx_Freeze
build_exe_options = {
    # Include only available packages
    "packages": available_packages + [
        "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "matplotlib.backends.backend_qtagg"
    ],

    # Include essential files
    "include_files": [
        ("data/", "data/"),
        ("modules/", "modules/"),
        ("utils/", "utils/"),
        ("__version__.py", "__version__.py"),
        ("version.py", "version.py"),
        ("varsys_branding.py", "varsys_branding.py")
    ],

    # Exclude problematic packages
    "excludes": [
        "tkinter", "unittest", "test", "distutils", "setuptools",
        "email", "html", "http", "xml", "xmlrpc",
        "pydoc", "doctest", "argparse", "difflib", "inspect",
        "pdb", "profile", "pstats", "timeit", "trace"
    ],

    # Build directory
    "build_exe": f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",

    # Optimize for size and performance
    "optimize": 2,
    
    # Silent build
    "silent": True
}

# Add optional files if they exist
optional_files = [
    ("assets/", "assets/"),
    ("logs/", "logs/"),
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE"),
    ("config.py", "config.py"),
    ("varsys_config.py", "varsys_config.py")
]

# Add Firebase files only if Firebase is available
if firebase_available:
    optional_files.extend([
        ("firebase_config.json", "firebase_config.json"),
        ("firebase_web_config.json", "firebase_web_config.json"),
        ("jwt_secret.key", "jwt_secret.key")
    ])

# Add files that actually exist
for src, dst in optional_files:
    if os.path.exists(src):
        build_exe_options["include_files"].append((src, dst))
        print(f"✓ Including {src}")
    else:
        print(f"- Skipping {src} (not found)")

# MSI installer options
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-9012-123456789012}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\VARSYS\Kitchen Dashboard"
}

if ICON_FILE:
    bdist_msi_options["install_icon"] = ICON_FILE

# Create executable
base = None
if platform.system() == "Windows":
    base = "Win32GUI"  # Hide console window

# Define the executable
executable_options = {
    "script": MAIN_SCRIPT,
    "base": base,
    "target_name": "VARSYS_Kitchen_Dashboard.exe",
    "copyright": APP_COPYRIGHT,
    "trademarks": "VARSYS Kitchen Dashboard"
}

if ICON_FILE:
    executable_options["icon"] = ICON_FILE

executable = Executable(**executable_options)

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
=== Minimal Build Configuration ===
Application: {APP_NAME} v{APP_VERSION}
Python Version: {sys.version}
Platform: {platform.system()} {platform.architecture()[0]}
Build Tool: cx_Freeze (Minimal)
Firebase: {'Enabled' if firebase_available else 'Disabled'}
Icon: {ICON_FILE if ICON_FILE else 'Default'}
Output: VARSYS_Kitchen_Dashboard.exe

Packages included: {len(available_packages)}
Files included: {len(build_exe_options['include_files'])}

Build directory: {build_exe_options['build_exe']}

To build:
1. python setup_cx_freeze_minimal.py build
2. Test: cd {build_exe_options['build_exe']} && VARSYS_Kitchen_Dashboard.exe
""")
