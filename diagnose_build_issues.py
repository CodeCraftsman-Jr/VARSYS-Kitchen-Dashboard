#!/usr/bin/env python3
"""
Diagnostic script for Kitchen Dashboard build issues
Identifies specific problems causing cx_Freeze failures
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{colors.get(status, 'ℹ️')} {message}")

def check_environment():
    """Check Python environment and basic setup"""
    print_header("ENVIRONMENT CHECK")
    
    # Python version
    version = sys.version_info
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}", "info")
    
    if version.major != 3:
        print_status("Python 3.x required", "error")
        return False
    
    if version.minor < 8:
        print_status("Python 3.8+ recommended for best compatibility", "warning")
    
    # Platform
    print_status(f"Platform: {sys.platform}", "info")
    
    # Working directory
    print_status(f"Working directory: {os.getcwd()}", "info")
    
    # Check if main script exists
    if os.path.exists("kitchen_app.py"):
        print_status("Main script (kitchen_app.py) found", "success")
    else:
        print_status("Main script (kitchen_app.py) NOT found", "error")
        return False
    
    return True

def check_critical_packages():
    """Check critical package installations"""
    print_header("PACKAGE INSTALLATION CHECK")
    
    critical_packages = [
        "pandas", "numpy", "matplotlib", "PySide6", "cx_Freeze", 
        "urllib3", "requests", "setuptools", "wheel"
    ]
    
    installed_packages = {}
    missing_packages = []
    
    for package in critical_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                installed_packages[package] = version
                print_status(f"{package}: {version}", "success")
            else:
                missing_packages.append(package)
                print_status(f"{package}: NOT FOUND", "error")
        except Exception as e:
            missing_packages.append(package)
            print_status(f"{package}: ERROR - {e}", "error")
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "warning")
        return False, missing_packages
    
    return True, installed_packages

def check_problematic_imports():
    """Check for specific imports that cause cx_Freeze issues"""
    print_header("PROBLEMATIC IMPORTS CHECK")
    
    # Test imports that commonly cause issues
    problematic_imports = [
        ("pandas.core.api", "pandas core API"),
        ("pandas.core.groupby", "pandas groupby"),
        ("pandas.core.frame", "pandas DataFrame"),
        ("pandas.core.generic", "pandas generic"),
        ("pandas.io.formats.format", "pandas format"),
        ("pandas.io.common", "pandas IO common"),
        ("urllib.parse", "urllib parse"),
        ("http.client", "HTTP client"),
        ("matplotlib.backends.backend_qtagg", "matplotlib Qt backend")
    ]
    
    working_imports = []
    failing_imports = []
    
    for import_name, description in problematic_imports:
        try:
            __import__(import_name)
            working_imports.append(import_name)
            print_status(f"{description}: OK", "success")
        except ImportError as e:
            failing_imports.append((import_name, str(e)))
            print_status(f"{description}: FAILED - {e}", "warning")
        except Exception as e:
            failing_imports.append((import_name, str(e)))
            print_status(f"{description}: ERROR - {e}", "error")
    
    return working_imports, failing_imports

def check_build_files():
    """Check for build configuration files"""
    print_header("BUILD FILES CHECK")
    
    build_files = [
        "setup_cx_freeze.py",
        "setup_cx_freeze_fixed.py", 
        "setup_cx_freeze_minimal.py",
        "setup_ultra_minimal.py",
        "build_simple.py",
        "quick_build_fix.bat"
    ]
    
    found_files = []
    missing_files = []
    
    for build_file in build_files:
        if os.path.exists(build_file):
            found_files.append(build_file)
            print_status(f"{build_file}: Found", "success")
        else:
            missing_files.append(build_file)
            print_status(f"{build_file}: Missing", "warning")
    
    return found_files, missing_files

def check_data_directories():
    """Check for required data directories"""
    print_header("DATA DIRECTORIES CHECK")
    
    required_dirs = ["data", "modules", "utils"]
    optional_dirs = ["assets", "tests", "release"]
    
    found_dirs = []
    missing_dirs = []
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            file_count = len(list(Path(dir_name).rglob("*")))
            found_dirs.append(dir_name)
            print_status(f"{dir_name}/: Found ({file_count} files)", "success")
        else:
            missing_dirs.append(dir_name)
            print_status(f"{dir_name}/: Missing", "error")
    
    for dir_name in optional_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            file_count = len(list(Path(dir_name).rglob("*")))
            print_status(f"{dir_name}/: Found ({file_count} files)", "info")
    
    return found_dirs, missing_dirs

def test_simple_build():
    """Test a simple cx_Freeze build to identify specific errors"""
    print_header("SIMPLE BUILD TEST")
    
    # Create a minimal test script
    test_script = """
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["PySide6.QtWidgets"],
    "excludes": ["tkinter"]
}

executable = Executable(
    script="kitchen_app.py",
    target_name="test_build.exe"
)

setup(
    name="Test Build",
    version="1.0",
    options={"build_exe": build_exe_options},
    executables=[executable]
)
"""
    
    with open("test_build_setup.py", "w") as f:
        f.write(test_script)
    
    print_status("Created test build script", "info")
    
    try:
        result = subprocess.run([
            sys.executable, "test_build_setup.py", "build"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print_status("Simple build test PASSED", "success")
            return True, "Build successful"
        else:
            print_status("Simple build test FAILED", "error")
            print("Error output:")
            print(result.stderr)
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print_status("Build test timed out", "error")
        return False, "Timeout"
    except Exception as e:
        print_status(f"Build test error: {e}", "error")
        return False, str(e)
    finally:
        # Clean up
        if os.path.exists("test_build_setup.py"):
            os.remove("test_build_setup.py")

def generate_recommendations(results):
    """Generate recommendations based on diagnostic results"""
    print_header("RECOMMENDATIONS")
    
    env_ok, packages_result, imports_result, build_files, data_dirs, build_test = results
    
    if not env_ok:
        print_status("Fix environment issues first", "error")
        return
    
    packages_ok, package_info = packages_result
    if not packages_ok:
        print_status("Install missing packages:", "warning")
        if isinstance(package_info, list):  # missing packages
            for package in package_info:
                print(f"  pip install {package}")
    
    working_imports, failing_imports = imports_result
    if failing_imports:
        print_status("Import issues detected:", "warning")
        print("  These imports may need to be excluded in cx_Freeze build:")
        for import_name, error in failing_imports:
            print(f"    {import_name}")
    
    found_build_files, missing_build_files = build_files
    if not found_build_files:
        print_status("No build files found - create setup scripts", "error")
    else:
        print_status(f"Use available build files: {found_build_files[0]}", "info")
    
    build_success, build_error = build_test
    if not build_success:
        print_status("Build test failed - check error details above", "error")
        if "pandas" in build_error.lower():
            print_status("Pandas-related build error detected", "warning")
            print("  Try: pip install 'pandas>=1.5.0,<2.1.0' --force-reinstall")
        if "urllib" in build_error.lower():
            print_status("urllib-related build error detected", "warning") 
            print("  Try: pip install 'urllib3>=1.26.0,<2.0' --force-reinstall")

def main():
    """Main diagnostic function"""
    print_header("KITCHEN DASHBOARD BUILD DIAGNOSTIC")
    print("This script will identify issues preventing successful builds")
    
    # Run all diagnostic checks
    env_ok = check_environment()
    packages_result = check_critical_packages()
    imports_result = check_problematic_imports()
    build_files = check_build_files()
    data_dirs = check_data_directories()
    build_test = test_simple_build()
    
    # Generate recommendations
    results = (env_ok, packages_result, imports_result, build_files, data_dirs, build_test)
    generate_recommendations(results)
    
    print_header("DIAGNOSTIC COMPLETE")
    print("Review the recommendations above to fix build issues.")
    print("\nNext steps:")
    print("1. Fix any critical issues identified")
    print("2. Run: fix_build_comprehensive.bat")
    print("3. If still failing, check PANDAS_BUILD_ERROR_GUIDE.md")

if __name__ == "__main__":
    main()
