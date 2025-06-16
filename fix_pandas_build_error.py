#!/usr/bin/env python3
"""
Fix pandas build errors in cx_Freeze for Kitchen Dashboard v1.1.1
Resolves pandas import issues and missing modules
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def print_status(message, status="info"):
    """Print status with icons"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def clean_build_environment():
    """Clean build environment completely"""
    print("=" * 60)
    print("CLEANING BUILD ENVIRONMENT")
    print("=" * 60)
    
    dirs_to_clean = ["build", "dist", "__pycache__", ".pytest_cache"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print_status(f"Cleaned {dir_name}", "success")
            except Exception as e:
                print_status(f"Could not clean {dir_name}: {e}", "warning")
    
    # Clean Python cache files
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass
        for dir_name in dirs[:]:
            if dir_name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, dir_name))
                    dirs.remove(dir_name)
                except:
                    pass

def install_compatible_packages():
    """Install compatible versions of problematic packages"""
    print("\n" + "=" * 60)
    print("INSTALLING COMPATIBLE PACKAGES")
    print("=" * 60)
    
    # Compatible package versions that work with cx_Freeze
    packages = [
        # Core packages with specific versions
        ("pandas", "pandas>=1.5.0,<2.1.0"),  # Avoid pandas 2.1+ issues
        ("numpy", "numpy>=1.21.0,<1.25.0"),  # Compatible numpy
        ("matplotlib", "matplotlib>=3.5.0,<3.8.0"),  # Stable matplotlib
        
        # urllib3 and requests (fixed versions)
        ("urllib3", "urllib3>=1.26.0,<2.0"),  # Avoid urllib3 2.0+ issues
        ("requests", "requests>=2.25.0,<3.0"),  # Compatible requests
        
        # Build tools
        ("cx_Freeze", "cx_Freeze>=6.15.0"),  # Latest cx_Freeze
        ("setuptools", "setuptools>=65.0.0"),  # Updated setuptools
        ("wheel", "wheel>=0.38.0"),  # Updated wheel
        
        # UI framework
        ("PySide6", "PySide6>=6.4.0,<6.6.0"),  # Stable PySide6
        
        # Optional packages
        ("openpyxl", "openpyxl>=3.0.0"),
        ("Pillow", "Pillow>=9.0.0"),
        ("python-dateutil", "python-dateutil>=2.8.0"),
        ("certifi", "certifi>=2022.12.7")
    ]
    
    print_status(f"Installing {len(packages)} compatible packages...", "info")
    
    success_count = 0
    failed_packages = []
    
    for package_name, pip_spec in packages:
        try:
            print_status(f"Installing {pip_spec}...", "info")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", pip_spec, "--force-reinstall"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_status(f"{package_name} installed successfully", "success")
                success_count += 1
            else:
                print_status(f"Failed to install {package_name}", "error")
                failed_packages.append(package_name)
                
        except subprocess.TimeoutExpired:
            print_status(f"Timeout installing {package_name}", "error")
            failed_packages.append(package_name)
        except Exception as e:
            print_status(f"Error installing {package_name}: {e}", "error")
            failed_packages.append(package_name)
    
    print_status(f"Package installation: {success_count}/{len(packages)} successful", 
                "success" if success_count >= len(packages) * 0.8 else "warning")
    
    if failed_packages:
        print_status(f"Failed packages: {', '.join(failed_packages)}", "warning")
    
    return success_count >= len(packages) * 0.8

def create_minimal_setup():
    """Create a minimal setup that avoids problematic imports"""
    print("\n" + "=" * 60)
    print("CREATING MINIMAL SETUP")
    print("=" * 60)
    
    minimal_setup_content = '''"""
Minimal cx_Freeze setup for Kitchen Dashboard v1.1.1
Avoids problematic pandas and urllib imports
"""

import sys
import os
from cx_Freeze import setup, Executable

# Application metadata
APP_NAME = "VARSYS Kitchen Dashboard"
APP_VERSION = "1.1.1"

# Main script
MAIN_SCRIPT = "kitchen_app.py"

# Minimal build configuration to avoid import issues
build_exe_options = {
    # Only include essential packages
    "packages": [
        "PySide6.QtWidgets", "PySide6.QtCore", "PySide6.QtGui",
        "pandas", "numpy", "matplotlib"
    ],
    
    # Essential files only
    "include_files": [
        ("data/", "data/"),
        ("modules/", "modules/"),
        ("utils/", "utils/"),
        ("__version__.py", "__version__.py")
    ],
    
    # Exclude problematic modules
    "excludes": [
        # Standard library modules that cause issues
        "tkinter", "unittest", "test", "email", "html", "http", 
        "urllib", "xml", "pydoc", "doctest", "distutils",
        
        # Pandas sub-modules that cause import issues
        "pandas.io.formats.format", "pandas.io.common", 
        "pandas.core.groupby.generic", "pandas.core.methods.describe",
        
        # Other problematic modules
        "matplotlib.backends.backend_tkagg", "IPython", "jupyter",
        "sphinx", "pytest", "setuptools"
    ],
    
    # Build settings
    "build_exe": f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",
    "optimize": 1,
    "include_msvcrt": True,
    
    # Avoid zip files to prevent import issues
    "zip_include_packages": [],
    "zip_exclude_packages": ["*"],
    
    # Replace problematic paths
    "replace_paths": [("*", "")]
}

# Create executable
executable = Executable(
    script=MAIN_SCRIPT,
    base="Win32GUI" if sys.platform == "win32" else None,
    target_name="VARSYS_Kitchen_Dashboard.exe"
)

# Setup
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description="Kitchen Management System",
    options={"build_exe": build_exe_options},
    executables=[executable]
)
'''
    
    try:
        with open("setup_minimal_fixed.py", "w") as f:
            f.write(minimal_setup_content)
        print_status("Created minimal setup file", "success")
        return True
    except Exception as e:
        print_status(f"Error creating minimal setup: {e}", "error")
        return False

def test_pandas_imports():
    """Test pandas imports to identify issues"""
    print("\n" + "=" * 60)
    print("TESTING PANDAS IMPORTS")
    print("=" * 60)
    
    pandas_modules = [
        "pandas",
        "pandas.core",
        "pandas.io",
        "numpy",
        "matplotlib",
        "PySide6"
    ]
    
    success_count = 0
    
    for module in pandas_modules:
        try:
            __import__(module)
            print_status(f"{module}: Import successful", "success")
            success_count += 1
        except ImportError as e:
            print_status(f"{module}: Import failed - {e}", "error")
        except Exception as e:
            print_status(f"{module}: Error - {e}", "error")
    
    return success_count >= len(pandas_modules) * 0.8

def try_different_build_approaches():
    """Try different build approaches"""
    print("\n" + "=" * 60)
    print("TRYING DIFFERENT BUILD APPROACHES")
    print("=" * 60)
    
    build_scripts = [
        ("Minimal Fixed Setup", "setup_minimal_fixed.py"),
        ("Minimal Setup", "setup_cx_freeze_minimal.py"),
        ("Fixed Setup", "setup_cx_freeze_fixed.py"),
        ("Original Setup", "setup_cx_freeze.py")
    ]
    
    for approach_name, script_name in build_scripts:
        print_status(f"Trying {approach_name}...", "info")
        
        if not os.path.exists(script_name):
            if script_name == "setup_minimal_fixed.py":
                create_minimal_setup()
            else:
                print_status(f"{script_name} not found", "warning")
                continue
        
        try:
            # Clean before each attempt
            if os.path.exists("build"):
                shutil.rmtree("build")
            
            result = subprocess.run([
                sys.executable, script_name, "build"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print_status(f"{approach_name} succeeded!", "success")
                
                # Check if executable was created
                build_dirs = [
                    f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",
                    "build/exe.win-amd64-3.12",
                    "build/exe.win-amd64-3.13"
                ]
                
                for build_dir in build_dirs:
                    exe_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
                    if os.path.exists(exe_path):
                        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                        print_status(f"Executable created: {exe_path} ({size_mb:.1f} MB)", "success")
                        return True, approach_name
                
                print_status("Build succeeded but executable not found", "warning")
                
            else:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                print_status(f"{approach_name} failed: {error_msg}...", "error")
                
        except subprocess.TimeoutExpired:
            print_status(f"{approach_name} timed out", "error")
        except Exception as e:
            print_status(f"{approach_name} error: {e}", "error")
    
    return False, None

def create_build_report(success, method_used):
    """Create a build report"""
    report_content = f"""VARSYS Kitchen Dashboard v1.1.1 - Build Report
Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Build Status: {'SUCCESS' if success else 'FAILED'}
Method Used: {method_used if method_used else 'None'}

Issues Addressed:
- pandas import errors
- urllib3 compatibility
- cx_Freeze module detection
- Missing standard library modules

Packages Installed:
- pandas >= 1.5.0, < 2.1.0
- numpy >= 1.21.0, < 1.25.0
- urllib3 >= 1.26.0, < 2.0
- cx_Freeze >= 6.15.0
- PySide6 >= 6.4.0, < 6.6.0

Build Configuration:
- Excluded problematic pandas sub-modules
- Avoided zip packaging
- Used conservative optimization
- Included essential files only

Next Steps:
"""
    
    if success:
        report_content += """1. Test the executable in the build directory
2. Create installer with Inno Setup
3. Test Firebase features if enabled
4. Deploy the application
"""
    else:
        report_content += """1. Check Python version (3.11 recommended)
2. Try PyInstaller as alternative
3. Use virtual environment
4. Check system dependencies
"""
    
    with open("build_report.txt", "w") as f:
        f.write(report_content)
    
    print_status("Build report saved: build_report.txt", "info")

def main():
    """Main fix function"""
    print("VARSYS Kitchen Dashboard v1.1.1 - Pandas Build Error Fix")
    print("=" * 60)
    
    # Step 1: Clean environment
    clean_build_environment()
    
    # Step 2: Install compatible packages
    if not install_compatible_packages():
        print_status("Package installation failed", "error")
        return False
    
    # Step 3: Test pandas imports
    if not test_pandas_imports():
        print_status("Pandas imports still have issues", "warning")
    
    # Step 4: Try different build approaches
    success, method = try_different_build_approaches()
    
    # Step 5: Create report
    create_build_report(success, method)
    
    print("\n" + "=" * 60)
    print("PANDAS BUILD FIX SUMMARY")
    print("=" * 60)
    
    if success:
        print_status(f"✅ BUILD SUCCESSFUL using {method}!", "success")
        print_status("Executable is ready in the build directory", "success")
    else:
        print_status("❌ All build methods failed", "error")
        print_status("Consider using PyInstaller or Python 3.11", "info")
    
    return success

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)
