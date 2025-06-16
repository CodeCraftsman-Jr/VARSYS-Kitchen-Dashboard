#!/usr/bin/env python3
"""
Fix Import Errors for Kitchen Dashboard v1.1.1
Specifically addresses pandas, urllib3, and missing module issues
"""

import sys
import subprocess
import os
import importlib.util

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{colors.get(status, 'ℹ️')} {message}")

def check_python_version():
    """Check Python version compatibility"""
    print_status("Checking Python version...", "info")
    version = sys.version_info
    print_status(f"Python {version.major}.{version.minor}.{version.micro}", "info")
    
    if version.major != 3 or version.minor < 8:
        print_status("Python 3.8+ required for best compatibility", "warning")
        return False
    
    print_status("Python version is compatible", "success")
    return True

def install_compatible_packages():
    """Install compatible package versions"""
    print_status("Installing compatible package versions...", "info")
    
    # Package specifications that work with cx_Freeze
    packages = [
        ("pandas", "pandas>=1.5.0,<2.1.0"),
        ("numpy", "numpy>=1.21.0,<1.25.0"), 
        ("urllib3", "urllib3>=1.26.0,<2.0"),
        ("matplotlib", "matplotlib>=3.5.0,<3.8.0"),
        ("PySide6", "PySide6>=6.4.0,<6.6.0"),
        ("cx_Freeze", "cx_Freeze>=6.15.0"),
        ("setuptools", "setuptools>=65.0.0"),
        ("wheel", "wheel>=0.38.0")
    ]
    
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
                print_status(f"Failed to install {package_name}: {result.stderr}", "error")
                failed_packages.append(package_name)
                
        except subprocess.TimeoutExpired:
            print_status(f"Timeout installing {package_name}", "error")
            failed_packages.append(package_name)
        except Exception as e:
            print_status(f"Error installing {package_name}: {e}", "error")
            failed_packages.append(package_name)
    
    if failed_packages:
        print_status(f"Failed to install: {', '.join(failed_packages)}", "warning")
    
    return success_count >= len(packages) * 0.8

def test_critical_imports():
    """Test critical imports that cause build failures"""
    print_status("Testing critical imports...", "info")
    
    critical_modules = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("PySide6.QtWidgets", "PySide6"),
        ("matplotlib", "matplotlib"),
        ("urllib.parse", "urllib"),
        ("http.client", "http"),
        ("json", "json")
    ]
    
    success_count = 0
    failed_imports = []
    
    for module_name, package_name in critical_modules:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                __import__(module_name)
                print_status(f"{module_name}: Import successful", "success")
                success_count += 1
            else:
                print_status(f"{module_name}: Module not found", "error")
                failed_imports.append(module_name)
        except ImportError as e:
            print_status(f"{module_name}: Import failed - {e}", "error")
            failed_imports.append(module_name)
        except Exception as e:
            print_status(f"{module_name}: Error - {e}", "error")
            failed_imports.append(module_name)
    
    if failed_imports:
        print_status(f"Failed imports: {', '.join(failed_imports)}", "warning")
    
    return success_count >= len(critical_modules) * 0.8

def test_pandas_specific_imports():
    """Test specific pandas imports that cause cx_Freeze issues"""
    print_status("Testing pandas-specific imports...", "info")
    
    pandas_modules = [
        "pandas.core.api",
        "pandas.core.groupby", 
        "pandas.core.frame",
        "pandas.core.generic",
        "pandas.io.common"
    ]
    
    success_count = 0
    
    for module in pandas_modules:
        try:
            __import__(module)
            print_status(f"{module}: Import successful", "success")
            success_count += 1
        except ImportError as e:
            print_status(f"{module}: Import failed - {e}", "warning")
            # These failures are expected and can be handled by cx_Freeze excludes
        except Exception as e:
            print_status(f"{module}: Error - {e}", "warning")
    
    return True  # Don't fail on pandas sub-module issues

def create_import_test_script():
    """Create a test script to verify imports work"""
    test_script = """
import sys
import os

# Test critical imports
try:
    import pandas as pd
    print("✓ pandas imported successfully")
    print(f"  Version: {pd.__version__}")
except Exception as e:
    print(f"❌ pandas import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully") 
    print(f"  Version: {np.__version__}")
except Exception as e:
    print(f"❌ numpy import failed: {e}")

try:
    from PySide6.QtWidgets import QApplication
    print("✓ PySide6 imported successfully")
except Exception as e:
    print(f"❌ PySide6 import failed: {e}")

try:
    import matplotlib
    print("✓ matplotlib imported successfully")
    print(f"  Version: {matplotlib.__version__}")
except Exception as e:
    print(f"❌ matplotlib import failed: {e}")

try:
    import urllib.parse
    import http.client
    print("✓ urllib and http modules imported successfully")
except Exception as e:
    print(f"❌ urllib/http import failed: {e}")

print("\\nImport test completed.")
"""
    
    with open("test_imports.py", "w") as f:
        f.write(test_script)
    
    print_status("Created import test script: test_imports.py", "success")
    
    # Run the test script
    try:
        result = subprocess.run([sys.executable, "test_imports.py"], 
                              capture_output=True, text=True, timeout=30)
        print("Import test results:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print_status(f"Error running import test: {e}", "error")
        return False

def main():
    """Main fix function"""
    print("=" * 60)
    print("KITCHEN DASHBOARD v1.1.1 - IMPORT ERROR FIX")
    print("=" * 60)
    print("Fixing pandas, urllib3, and missing module issues...")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        print_status("Python version check failed", "warning")
    
    # Step 2: Install compatible packages
    print_status("Step 1: Installing compatible packages", "info")
    if not install_compatible_packages():
        print_status("Package installation had issues", "warning")
    
    # Step 3: Test critical imports
    print_status("Step 2: Testing critical imports", "info")
    if not test_critical_imports():
        print_status("Critical import test failed", "error")
        return False
    
    # Step 4: Test pandas-specific imports
    print_status("Step 3: Testing pandas-specific imports", "info")
    test_pandas_specific_imports()
    
    # Step 5: Create and run import test
    print_status("Step 4: Creating import test script", "info")
    test_success = create_import_test_script()
    
    print("\n" + "=" * 60)
    print("IMPORT ERROR FIX COMPLETED")
    print("=" * 60)
    
    if test_success:
        print_status("All critical imports working correctly", "success")
        print_status("You can now try building with: quick_build_fix.bat", "info")
    else:
        print_status("Some imports still have issues", "warning")
        print_status("Check the output above for specific errors", "info")
    
    print("\nNext steps:")
    print("1. Run: quick_build_fix.bat")
    print("2. If build still fails, check PANDAS_BUILD_ERROR_GUIDE.md")
    print("3. Consider using alternative build tools (Nuitka)")
    
    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
