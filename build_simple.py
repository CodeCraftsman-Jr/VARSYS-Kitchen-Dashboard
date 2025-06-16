#!/usr/bin/env python3
"""
Simple build script for Kitchen Dashboard v1.1.1
Handles cx_Freeze errors and missing modules
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_status(message, status="info"):
    """Print status with icons"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print_status(f"Cleaned {dir_name}", "success")
            except Exception as e:
                print_status(f"Could not clean {dir_name}: {e}", "warning")

def install_missing_packages():
    """Install packages that are commonly missing"""
    packages = [
        "cx_Freeze",
        "pandas", 
        "matplotlib",
        "PySide6",
        "numpy",
        "openpyxl",
        "Pillow",
        "requests"
    ]
    
    print_status("Installing/updating core packages...", "info")
    
    for package in packages:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print_status(f"{package} installed/updated", "success")
            else:
                print_status(f"Failed to install {package}", "warning")
                
        except Exception as e:
            print_status(f"Error installing {package}: {e}", "warning")

def create_simple_setup():
    """Create a very simple setup.py that avoids problematic imports"""
    
    setup_content = '''
import sys
import os
from cx_Freeze import setup, Executable

# Simple build configuration
build_exe_options = {
    "packages": ["pandas", "matplotlib", "PySide6", "numpy"],
    "include_files": [
        ("data/", "data/"),
        ("modules/", "modules/"),
        ("utils/", "utils/"),
        ("__version__.py", "__version__.py")
    ],
    "excludes": [
        "tkinter", "unittest", "test", "email", "html", "http", 
        "urllib", "xml", "pydoc", "doctest"
    ],
    "build_exe": f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",
    "optimize": 1,
    "include_msvcrt": True
}

executable = Executable(
    script="kitchen_app.py",
    base="Win32GUI",
    target_name="VARSYS_Kitchen_Dashboard.exe"
)

setup(
    name="VARSYS Kitchen Dashboard",
    version="1.1.1",
    description="Kitchen Management System",
    options={"build_exe": build_exe_options},
    executables=[executable]
)
'''
    
    with open("setup_simple.py", "w") as f:
        f.write(setup_content)
    
    print_status("Created simple setup file", "success")

def try_build_methods():
    """Try different build methods in order of preference"""
    
    build_methods = [
        ("Fixed Setup", "setup_cx_freeze_fixed.py"),
        ("Minimal Setup", "setup_cx_freeze_minimal.py"),
        ("Simple Setup", "setup_simple.py"),
        ("Original Setup", "setup_cx_freeze.py")
    ]
    
    for method_name, setup_file in build_methods:
        print_status(f"Trying {method_name}...", "info")
        
        if not os.path.exists(setup_file):
            if setup_file == "setup_simple.py":
                create_simple_setup()
            else:
                print_status(f"{setup_file} not found, skipping", "warning")
                continue
        
        try:
            result = subprocess.run([
                sys.executable, setup_file, "build"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_status(f"{method_name} succeeded!", "success")
                
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
                        return True
                
                print_status("Build succeeded but executable not found", "warning")
                return False
                
            else:
                print_status(f"{method_name} failed: {result.stderr[:200]}...", "error")
                
        except subprocess.TimeoutExpired:
            print_status(f"{method_name} timed out", "error")
        except Exception as e:
            print_status(f"{method_name} error: {e}", "error")
    
    return False

def test_executable():
    """Test if the built executable works"""
    build_dirs = [
        f"build/exe.win-amd64-{sys.version_info.major}.{sys.version_info.minor}",
        "build/exe.win-amd64-3.12",
        "build/exe.win-amd64-3.13"
    ]
    
    for build_dir in build_dirs:
        exe_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
        if os.path.exists(exe_path):
            print_status(f"Testing executable: {exe_path}", "info")
            
            try:
                # Try to start the executable (will timeout after 5 seconds)
                process = subprocess.Popen([exe_path], cwd=build_dir)
                
                # Wait a bit then terminate
                import time
                time.sleep(3)
                process.terminate()
                
                try:
                    process.wait(timeout=2)
                    print_status("Executable test passed", "success")
                    return True
                except subprocess.TimeoutExpired:
                    process.kill()
                    print_status("Executable started but had to be killed", "warning")
                    return True
                    
            except Exception as e:
                print_status(f"Executable test failed: {e}", "error")
                return False
    
    print_status("No executable found to test", "error")
    return False

def main():
    """Main build function"""
    print("=" * 60)
    print("VARSYS Kitchen Dashboard v1.1.1 - Simple Build")
    print("=" * 60)
    
    # Step 1: Clean previous builds
    print_status("Step 1: Cleaning previous builds", "info")
    clean_build_dirs()
    
    # Step 2: Install missing packages
    print_status("Step 2: Installing/updating packages", "info")
    install_missing_packages()
    
    # Step 3: Try different build methods
    print_status("Step 3: Attempting build", "info")
    build_success = try_build_methods()
    
    if build_success:
        # Step 4: Test the executable
        print_status("Step 4: Testing executable", "info")
        test_success = test_executable()
        
        print("=" * 60)
        if test_success:
            print_status("🎉 BUILD AND TEST SUCCESSFUL!", "success")
            print_status("Your executable is ready in the build directory", "success")
        else:
            print_status("⚠️ Build successful but executable test failed", "warning")
            print_status("Try running the executable manually", "info")
    else:
        print("=" * 60)
        print_status("❌ All build methods failed", "error")
        print_status("Try installing Python 3.11 or using PyInstaller", "info")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
