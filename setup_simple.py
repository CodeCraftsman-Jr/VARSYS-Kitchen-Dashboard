"""
Robust cx_Freeze setup for Kitchen Dashboard
"""

import sys
import os
from cx_Freeze import setup, Executable

# Check if files exist before including them
def safe_include_files():
    files_to_include = []

    # Required directories
    required_dirs = ["data", "modules", "utils", "assets"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            files_to_include.append((dir_name + "/", dir_name + "/"))

    # Optional files
    optional_files = [
        "firebase_config.json", "firebase_web_config.json", "jwt_secret.key",
        "__version__.py", "version.py", "config.py", "varsys_config.py", "varsys_branding.py"
    ]
    for file_name in optional_files:
        if os.path.exists(file_name):
            files_to_include.append((file_name, file_name))

    return files_to_include

# Robust build options
build_exe_options = {
    "packages": [
        "pandas", "matplotlib", "PySide6", "numpy", "PIL",
        "requests", "urllib3", "certifi", "openpyxl",
        "matplotlib.backends.backend_qtagg",
        "traceback", "sys", "os", "json", "csv", "datetime"
    ],
    "include_files": safe_include_files(),
    "excludes": ["tkinter", "unittest", "test", "distutils"],
    "include_msvcrt": False,
}

# Create executable with error handling
icon_file = "assets/icons/vasanthkitchen.ico" if os.path.exists("assets/icons/vasanthkitchen.ico") else None

executable = Executable(
    script="kitchen_app.py",
    base="Win32GUI",
    icon=icon_file,
    target_name="VARSYS_Kitchen_Dashboard.exe"
)

# Setup
setup(
    name="VARSYS Kitchen Dashboard",
    version="1.0.6",
    description="Kitchen Management System",
    options={"build_exe": build_exe_options},
    executables=[executable]
)

print("Robust build configuration loaded")
print(f"Including {len(build_exe_options['include_files'])} files/directories")
