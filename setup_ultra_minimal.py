"""
Ultra-minimal cx_Freeze setup for Kitchen Dashboard v1.1.1
Designed to avoid pandas import issues and complex dependencies
"""

import sys
import os
from cx_Freeze import setup, Executable

print("=" * 60)
print("ULTRA-MINIMAL BUILD CONFIGURATION")
print("=" * 60)

# Application metadata
APP_NAME = "VARSYS Kitchen Dashboard"
APP_VERSION = "1.1.1"
MAIN_SCRIPT = "kitchen_app.py"

# Check if main script exists
if not os.path.exists(MAIN_SCRIPT):
    print(f"❌ ERROR: {MAIN_SCRIPT} not found!")
    sys.exit(1)

print(f"✓ Main script: {MAIN_SCRIPT}")
print(f"✓ Python version: {sys.version}")

# Ultra-minimal build options to fix specific import errors
build_exe_options = {
    # Core packages - explicit inclusion to avoid auto-detection issues
    "packages": [
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "pandas",
        "numpy",
        "matplotlib"
    ],

    # Essential files only
    "include_files": [
        ("data/", "data/") if os.path.exists("data") else None,
        ("modules/", "modules/") if os.path.exists("modules") else None,
        ("utils/", "utils/") if os.path.exists("utils") else None,
        ("__version__.py", "__version__.py") if os.path.exists("__version__.py") else None,
        ("version.py", "version.py") if os.path.exists("version.py") else None,
        ("varsys_branding.py", "varsys_branding.py") if os.path.exists("varsys_branding.py") else None
    ],

    # Explicitly include modules that might be missing
    "includes": [
        # Standard library modules that are often missing
        "urllib", "urllib.parse", "urllib.request", "urllib.error",
        "http", "http.client",
        "json", "csv", "datetime", "calendar",
        "collections", "itertools", "functools",
        "pathlib", "tempfile", "shutil",
        "threading", "queue",

        # Pandas core modules (to fix pandas import errors)
        "pandas.core",
        "pandas.io",

        # Matplotlib backend
        "matplotlib.backends.backend_qtagg"
    ],

    # Exclude problematic modules that cause import conflicts
    "excludes": [
        # Standard library modules that cause cx_Freeze issues
        "tkinter", "unittest", "test", "distutils", "setuptools",
        "email", "html", "xml", "xmlrpc",
        "pydoc", "doctest", "argparse", "difflib", "inspect",
        "pdb", "profile", "pstats", "timeit", "trace",

        # Specific pandas sub-modules that cause import errors
        "pandas.io.formats.format",
        "pandas.io.common",
        "pandas.core.groupby.generic",
        "pandas.core.methods.describe",
        "pandas.core.groupby.groupby",
        "pandas.core.frame.DataFrame",

        # Matplotlib backends that cause issues
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends.backend_gtk3agg",

        # Other problematic modules
        "IPython", "jupyter", "sphinx", "pytest", "nose",
        "scipy", "sklearn", "seaborn",  # Optional heavy packages

        # Firebase (if causing issues)
        "firebase_admin", "pyrebase", "google.cloud"
    ],

    # Build directory
    "build_exe": f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",

    # Conservative settings to avoid issues
    "optimize": 0,  # No optimization to avoid import issues
    "include_msvcrt": True,

    # Avoid zip packaging completely to prevent import issues
    "zip_include_packages": [],
    "zip_exclude_packages": ["*"],

    # Include all files in directory structure (not in zip)
    "include_in_shared_zip": False,

    # Path replacement to avoid absolute paths
    "replace_paths": [("*", "")]
}

# Remove None entries from include_files
build_exe_options["include_files"] = [
    item for item in build_exe_options["include_files"] if item is not None
]

print(f"✓ Files to include: {len(build_exe_options['include_files'])}")
for src, dst in build_exe_options["include_files"]:
    print(f"  - {src} -> {dst}")

# Create executable with minimal options
executable_options = {
    "script": MAIN_SCRIPT,
    "target_name": "VARSYS_Kitchen_Dashboard.exe"
}

# Only add GUI base on Windows
if sys.platform == "win32":
    executable_options["base"] = "Win32GUI"

# Add icon if available
icon_file = "assets/icons/vasanthkitchen.ico"
if os.path.exists(icon_file):
    executable_options["icon"] = icon_file
    print(f"✓ Icon: {icon_file}")
else:
    print("- No icon file found")

executable = Executable(**executable_options)

print(f"✓ Target: {executable_options['target_name']}")
print(f"✓ Build directory: {build_exe_options['build_exe']}")

# MSI options (minimal)
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-5678-9012-123456789012}",
    "add_to_path": False
}

print("\n" + "=" * 60)
print("STARTING ULTRA-MINIMAL BUILD")
print("=" * 60)

try:
    setup(
        name=APP_NAME,
        version=APP_VERSION,
        description="Kitchen Management System (Minimal Build)",
        author="VARSYS",
        options={
            "build_exe": build_exe_options,
            "bdist_msi": bdist_msi_options
        },
        executables=[executable]
    )
    
    print("\n" + "=" * 60)
    print("BUILD CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Application: {APP_NAME} v{APP_VERSION}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Platform: {sys.platform}")
    print(f"Build type: Ultra-minimal (avoids pandas import issues)")
    print(f"Packages excluded: {len(build_exe_options['excludes'])}")
    print(f"Files included: {len(build_exe_options['include_files'])}")
    print(f"Output: {build_exe_options['build_exe']}")
    
    print("\nThis build:")
    print("✓ Avoids problematic pandas sub-modules")
    print("✓ Excludes urllib and http modules")
    print("✓ Uses no optimization to prevent import issues")
    print("✓ Avoids zip packaging")
    print("✓ Includes only essential files")
    
    print(f"\nTo test the build:")
    print(f"1. cd {build_exe_options['build_exe']}")
    print(f"2. {executable_options['target_name']}")

except Exception as e:
    print(f"\n❌ BUILD FAILED: {e}")
    print("\nTroubleshooting:")
    print("1. Check that all required packages are installed")
    print("2. Try: pip install --upgrade cx_Freeze")
    print("3. Try: pip install pandas==1.5.3 numpy==1.24.3")
    print("4. Consider using PyInstaller instead")
    raise
