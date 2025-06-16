#!/usr/bin/env python3
"""
Test script to verify build requirements and compatibility
Run this before building to catch potential issues
"""

import sys
import os
import importlib
import platform
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("=== Python Version Test ===")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version[:2] == (3, 12):
        print("✓ Python 3.12 - Fully supported")
        return True
    elif version[:2] == (3, 13):
        print("✓ Python 3.13 - Supported")
        return True
    else:
        print(f"⚠ Python {version.major}.{version.minor} - May have compatibility issues")
        print("Recommended: Python 3.12 or 3.13")
        return False

def test_required_files():
    """Test if all required files exist"""
    print("\n=== Required Files Test ===")
    
    required_files = [
        "kitchen_app.py",
        "setup_cx_freeze.py",
        "requirements.txt",
        "requirements_build.txt",
        "assets/icons/vasanthkitchen.ico",
        "modules/__init__.py",
        "utils/app_logger.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_core_imports():
    """Test if core dependencies can be imported"""
    print("\n=== Core Dependencies Test ===")
    
    core_modules = [
        "pandas",
        "matplotlib", 
        "PySide6",
        "numpy",
        "PIL",
        "requests"
    ]
    
    all_imported = True
    for module_name in core_modules:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name} - {e}")
            all_imported = False
    
    return all_imported

def test_build_tools():
    """Test if build tools are available"""
    print("\n=== Build Tools Test ===")
    
    try:
        import cx_Freeze
        print(f"✓ cx_Freeze {cx_Freeze.version}")
        cx_freeze_ok = True
    except ImportError:
        print("❌ cx_Freeze - Not installed")
        cx_freeze_ok = False
    
    try:
        import setuptools
        print(f"✓ setuptools {setuptools.__version__}")
        setuptools_ok = True
    except ImportError:
        print("❌ setuptools - Not installed")
        setuptools_ok = False
    
    return cx_freeze_ok and setuptools_ok

def main():
    """Run all tests"""
    print("VARSYS Kitchen Dashboard - Build Compatibility Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_required_files,
        test_core_imports,
        test_build_tools
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("✓ Ready to build!")
        return True
    else:
        print(f"❌ {total - passed} TESTS FAILED ({passed}/{total})")
        print("Please fix the issues above before building.")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\nTo fix common issues:")
        print("1. Install missing dependencies: pip install -r requirements_build.txt")
        print("2. Install cx_Freeze: pip install cx_Freeze")
        print("3. Create missing directories")
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
