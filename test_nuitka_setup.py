#!/usr/bin/env python3
"""
Test script to verify Nuitka setup and compatibility
Run this before attempting the full build
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def print_status(message, status_type="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",      # Blue
        "SUCCESS": "\033[92m",   # Green
        "WARNING": "\033[93m",   # Yellow
        "ERROR": "\033[91m",     # Red
        "RESET": "\033[0m"       # Reset
    }
    
    color = colors.get(status_type, colors["INFO"])
    reset = colors["RESET"]
    print(f"{color}[{status_type}] {message}{reset}")

def test_python_version():
    """Test Python version compatibility"""
    print_status("Testing Python version...", "INFO")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible", "SUCCESS")
        return True
    else:
        print_status(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported", "ERROR")
        print_status("Nuitka requires Python 3.8 or higher", "ERROR")
        return False

def test_nuitka_installation():
    """Test if Nuitka is installed and working"""
    print_status("Testing Nuitka installation...", "INFO")
    
    try:
        # Test import
        import nuitka
        print_status("✓ Nuitka module imported successfully", "SUCCESS")
        
        # Test command line
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print_status(f"✓ Nuitka command line working: {version}", "SUCCESS")
        return True
        
    except ImportError:
        print_status("❌ Nuitka module not found", "ERROR")
        print_status("Install with: pip install nuitka", "INFO")
        return False
    except subprocess.CalledProcessError:
        print_status("❌ Nuitka command line not working", "ERROR")
        return False
    except FileNotFoundError:
        print_status("❌ Nuitka command not found", "ERROR")
        return False

def test_required_dependencies():
    """Test if all required dependencies are available"""
    print_status("Testing required dependencies...", "INFO")
    
    required_packages = [
        ("PySide6", "PySide6"),
        ("pandas", "pandas"),
        ("numpy", "numpy"), 
        ("matplotlib", "matplotlib"),
        ("PIL", "Pillow"),
        ("openpyxl", "openpyxl"),
        ("requests", "requests")
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
            print_status(f"✓ {package_name} available", "SUCCESS")
        except ImportError:
            print_status(f"❌ {package_name} missing", "ERROR")
            missing_packages.append(package_name)
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
        print_status("Install with: pip install " + " ".join(missing_packages), "INFO")
        return False
    
    return True

def test_project_structure():
    """Test if project structure is correct"""
    print_status("Testing project structure...", "INFO")
    
    required_items = [
        ("kitchen_app.py", "file"),
        ("modules/", "directory"),
        ("utils/", "directory"),
        ("data/", "directory"),
        ("assets/", "directory")
    ]
    
    missing_items = []
    
    for item_path, item_type in required_items:
        path = Path(item_path)
        
        if item_type == "file" and path.is_file():
            print_status(f"✓ {item_path} found", "SUCCESS")
        elif item_type == "directory" and path.is_dir():
            print_status(f"✓ {item_path} found", "SUCCESS")
        else:
            print_status(f"❌ {item_path} missing", "ERROR")
            missing_items.append(item_path)
    
    if missing_items:
        print_status(f"Missing items: {', '.join(missing_items)}", "ERROR")
        return False
    
    return True

def test_icon_availability():
    """Test if application icon is available"""
    print_status("Testing application icon...", "INFO")
    
    icon_path = Path("assets/icons/vasanthkitchen.ico")
    
    if icon_path.exists():
        print_status(f"✓ Icon found: {icon_path}", "SUCCESS")
        return True
    else:
        print_status(f"⚠️ Icon not found: {icon_path}", "WARNING")
        print_status("Build will continue without custom icon", "WARNING")
        return True  # Not critical

def test_disk_space():
    """Test available disk space"""
    print_status("Testing available disk space...", "INFO")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        
        if free_gb >= 2.0:
            print_status(f"✓ Sufficient disk space: {free_gb:.1f} GB available", "SUCCESS")
            return True
        else:
            print_status(f"⚠️ Low disk space: {free_gb:.1f} GB available", "WARNING")
            print_status("Nuitka build may require 2GB+ free space", "WARNING")
            return True  # Warning, not error
            
    except Exception as e:
        print_status(f"Could not check disk space: {e}", "WARNING")
        return True

def test_simple_nuitka_build():
    """Test a simple Nuitka build to verify it works"""
    print_status("Testing simple Nuitka build...", "INFO")
    
    # Create a simple test script
    test_script = "test_simple.py"
    test_content = '''
import sys
print("Hello from Nuitka test!")
print(f"Python version: {sys.version}")
sys.exit(0)
'''
    
    try:
        # Write test script
        with open(test_script, 'w') as f:
            f.write(test_content)
        
        # Build with Nuitka
        cmd = [
            sys.executable, "-m", "nuitka",
            "--onefile",
            "--output-filename=test_simple.exe",
            "--output-dir=test_build",
            test_script
        ]
        
        print_status("Running simple Nuitka build test...", "INFO")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_status("✓ Simple Nuitka build successful", "SUCCESS")
            
            # Test the executable
            exe_path = Path("test_build/test_simple.exe")
            if exe_path.exists():
                print_status("✓ Test executable created", "SUCCESS")
                
                # Clean up
                import shutil
                if Path("test_build").exists():
                    shutil.rmtree("test_build")
                if Path(test_script).exists():
                    Path(test_script).unlink()
                if Path("test_simple.build").exists():
                    shutil.rmtree("test_simple.build")
                
                return True
            else:
                print_status("❌ Test executable not created", "ERROR")
                return False
        else:
            print_status("❌ Simple Nuitka build failed", "ERROR")
            print_status(f"Error: {result.stderr}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("❌ Simple build test timed out", "ERROR")
        return False
    except KeyboardInterrupt:
        print_status("⚠️ Simple build test interrupted by user", "WARNING")
        print_status("This is not critical - core tests passed", "INFO")
        return True  # Don't fail the entire test suite
    except Exception as e:
        print_status(f"❌ Simple build test failed: {e}", "ERROR")
        return False
    finally:
        # Clean up files
        for cleanup_path in [test_script, "test_build", "test_simple.build"]:
            try:
                path = Path(cleanup_path)
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)
            except:
                pass

def main():
    """Run all tests"""
    print_status("VARSYS Kitchen Dashboard - Nuitka Setup Test", "INFO")
    print_status("=" * 50, "INFO")
    
    tests = [
        ("Python Version", test_python_version),
        ("Nuitka Installation", test_nuitka_installation),
        ("Required Dependencies", test_required_dependencies),
        ("Project Structure", test_project_structure),
        ("Application Icon", test_icon_availability),
        ("Disk Space", test_disk_space),
        ("Simple Nuitka Build", test_simple_nuitka_build)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print_status(f"\nRunning test: {test_name}", "INFO")
        try:
            if test_func():
                passed += 1
            else:
                print_status(f"Test failed: {test_name}", "ERROR")
        except Exception as e:
            print_status(f"Test error: {test_name} - {e}", "ERROR")
    
    print_status("=" * 50, "INFO")
    print_status(f"Test Results: {passed}/{total} tests passed", "INFO")
    
    if passed == total:
        print_status("✅ All tests passed! Ready for Nuitka build.", "SUCCESS")
        print_status("You can now run: python setup_nuitka.py", "SUCCESS")
        return True
    else:
        print_status("❌ Some tests failed. Please fix issues before building.", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
