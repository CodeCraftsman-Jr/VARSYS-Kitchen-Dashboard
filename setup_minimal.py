"""
Minimal cx_Freeze setup for Kitchen Dashboard
"""

from cx_Freeze import setup, Executable
import os

# Minimal build options - only essential packages
build_exe_options = {
    "packages": ["pandas", "PySide6", "matplotlib"],
    "include_files": [
        ("data/", "data/"),
        ("modules/", "modules/"),
        ("utils/", "utils/")
    ] if os.path.exists("data") else [],
    "excludes": ["tkinter", "unittest", "test"],
}

# Create executable
executable = Executable(
    script="kitchen_app.py",
    base="Win32GUI",
    target_name="VARSYS_Kitchen_Dashboard.exe"
)

# Setup
setup(
    name="VARSYS Kitchen Dashboard",
    version="1.1.1",
    description="Kitchen Management System",
    options={"build_exe": build_exe_options},
    executables=[executable]
)

print("Minimal build configuration loaded")
