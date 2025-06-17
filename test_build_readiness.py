#!/usr/bin/env python3
"""
Test Build Readiness for VARSYS Kitchen Dashboard
Checks if the project is ready for cx_Freeze build

This script verifies:
- Python version compatibility
- Required dependencies
- File structure
- Import compatibility
- Potential build issues
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

def print_header(title):
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def print_check(description, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {description}")
    if details:
        print(f"   {details}")

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    
    version = sys.version_info
    compatible = version.major == 3 and version.minor >= 8
    
    print_check(
        f"Python {version.major}.{version.minor}.{version.micro}",
        compatible,
        "Compatible with cx_Freeze" if compatible else "Requires Python 3.8+"
    )
    
    return compatible

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Dependency Check")
    
    required_packages = [
        ("cx_Freeze", "cx_Freeze"),
        ("PySide6", "PySide6"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy"),
        ("requests", "requests"),
        ("Pillow", "PIL"),
        ("openpyxl", "openpyxl")
    ]
    
    optional_packages = [
        ("firebase-admin", "firebase_admin"),
        ("pyrebase4", "pyrebase"),
        ("PyJWT", "jwt"),
        ("cryptography", "cryptography"),
        ("scikit-learn", "sklearn"),
        ("seaborn", "seaborn")
    ]
    
    all_good = True
    
    print("Required packages:")
    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
            print_check(package_name, True, "Installed")
        except ImportError:
            print_check(package_name, False, "Missing - install required")
            all_good = False
    
    print("\nOptional packages:")
    for package_name, import_name in optional_packages:
        try:
            importlib.import_module(import_name)
            print_check(package_name, True, "Installed")
        except ImportError:
            print_check(package_name, False, "Missing - optional")
    
    return all_good

def check_file_structure():
    """Check if required files and directories exist"""
    print_header("File Structure Check")
    
    required_files = [
        "kitchen_app.py",
        "setup_cx_freeze.py",
        "requirements.txt"
    ]
    
    required_dirs = [
        "modules",
        "utils",
        "data"
    ]
    
    important_files = [
        "vasanthkitchen.ico",
        "firebase_config.json",
        "version.py",
        "__version__.py"
    ]
    
    all_good = True
    
    print("Required files:")
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print_check(file_path, exists)
        if not exists:
            all_good = False
    
    print("\nRequired directories:")
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        print_check(f"{dir_path}/", exists)
        if not exists:
            all_good = False
    
    print("\nImportant files:")
    for file_path in important_files:
        exists = os.path.exists(file_path)
        print_check(file_path, exists, "Found" if exists else "Missing")
    
    return all_good

def check_imports():
    """Check if main application imports work"""
    print_header("Import Compatibility Check")
    
    try:
        # Test basic imports that kitchen_app.py uses
        import pandas
        print_check("pandas import", True)
        
        import matplotlib
        print_check("matplotlib import", True)
        
        from PySide6.QtWidgets import QApplication
        print_check("PySide6.QtWidgets import", True)
        
        from PySide6.QtCore import Qt
        print_check("PySide6.QtCore import", True)
        
        from PySide6.QtGui import QFont
        print_check("PySide6.QtGui import", True)
        
        # Test if we can import our modules
        sys.path.insert(0, os.path.join(os.getcwd(), 'modules'))
        sys.path.insert(0, os.path.join(os.getcwd(), 'utils'))
        
        try:
            from utils.app_logger import get_logger
            print_check("utils.app_logger import", True)
        except ImportError as e:
            print_check("utils.app_logger import", False, str(e))
        
        try:
            from modules.modern_theme import ModernTheme
            print_check("modules.modern_theme import", True)
        except ImportError as e:
            print_check("modules.modern_theme import", False, str(e))
        
        return True
        
    except ImportError as e:
        print_check("Basic imports", False, str(e))
        return False

def check_cx_freeze_compatibility():
    """Check cx_Freeze specific compatibility"""
    print_header("cx_Freeze Compatibility Check")
    
    try:
        import cx_Freeze
        version = getattr(cx_Freeze, '__version__', 'Unknown')
        print_check(f"cx_Freeze {version}", True, "Available")
        
        # Check if we can import Executable
        from cx_Freeze import Executable
        print_check("cx_Freeze.Executable", True, "Import successful")
        
        # Check if setup_cx_freeze.py is valid Python
        if os.path.exists("setup_cx_freeze.py"):
            try:
                with open("setup_cx_freeze.py", 'r') as f:
                    content = f.read()
                compile(content, "setup_cx_freeze.py", "exec")
                print_check("setup_cx_freeze.py syntax", True, "Valid Python syntax")
            except SyntaxError as e:
                print_check("setup_cx_freeze.py syntax", False, f"Syntax error: {e}")
                return False
        
        return True
        
    except ImportError:
        print_check("cx_Freeze", False, "Not installed")
        return False

def run_build_test():
    """Run a dry-run test of the build process"""
    print_header("Build Process Test")
    
    if not os.path.exists("setup_cx_freeze.py"):
        print_check("Build script", False, "setup_cx_freeze.py not found")
        return False
    
    try:
        # Test if we can run the setup script with --help
        result = subprocess.run([
            sys.executable, "setup_cx_freeze.py", "--help"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_check("Build script execution", True, "Can run setup script")
            return True
        else:
            print_check("Build script execution", False, f"Error: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print_check("Build script execution", False, "Timeout")
        return False
    except Exception as e:
        print_check("Build script execution", False, str(e))
        return False

def main():
    """Main test function"""
    print_header("VARSYS Kitchen Dashboard - Build Readiness Test")
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Import Compatibility", check_imports),
        ("cx_Freeze Compatibility", check_cx_freeze_compatibility),
        ("Build Process", run_build_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print_check(f"{test_name}", result, status)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Your project is ready for cx_Freeze build!")
        print("Run: python build_complete.py")
    else:
        print(f"\n⚠️  {total - passed} issues need to be resolved before building")
        print("Please fix the failed tests and try again")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
