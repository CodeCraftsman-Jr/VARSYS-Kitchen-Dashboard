#!/usr/bin/env python3
"""
Complete Build Script for VARSYS Kitchen Dashboard
Handles the entire build process from cleanup to final executable

This script:
1. Cleans previous builds
2. Verifies all required files
3. Builds executable with cx_Freeze
4. Verifies the build
5. Provides next steps for installer creation
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n🔸 Step {step_num}: {description}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠️  {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print_error(f"Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_required_files():
    """Check if all required files exist"""
    print_step("1", "Checking required files")
    
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
    
    missing_files = []
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            missing_files.append(file_path)
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_success(f"Found: {dir_path}/")
        else:
            print_warning(f"Missing: {dir_path}/ (will be created)")
            os.makedirs(dir_path, exist_ok=True)
    
    if missing_files:
        print_error(f"Missing {len(missing_files)} required files. Build cannot continue.")
        return False
    
    print_success("All required files found")
    return True

def clean_previous_builds():
    """Clean previous build artifacts"""
    print_step("2", "Cleaning previous builds")
    
    paths_to_clean = [
        "build",
        "dist", 
        "__pycache__",
        "modules/__pycache__",
        "utils/__pycache__",
        "tests/__pycache__"
    ]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print_success(f"Removed directory: {path}")
                else:
                    os.remove(path)
                    print_success(f"Removed file: {path}")
            except Exception as e:
                print_warning(f"Could not remove {path}: {e}")
        else:
            print(f"   {path} (not found)")
    
    print_success("Build cleanup completed")

def install_dependencies():
    """Install required dependencies"""
    print_step("3", "Installing dependencies")
    
    try:
        # Install cx_Freeze if not already installed
        print("Installing cx_Freeze...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "cx_Freeze>=6.15.0"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("cx_Freeze installed/updated")
        else:
            print_warning("cx_Freeze installation had issues, but continuing...")
        
        # Install other requirements
        if os.path.exists("requirements.txt"):
            print("Installing project requirements...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success("Project requirements installed")
            else:
                print_warning("Some requirements may have failed to install")
                print(f"Error output: {result.stderr[:200]}...")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def build_executable():
    """Build the executable using cx_Freeze"""
    print_step("4", "Building executable with cx_Freeze")
    
    try:
        print("Running cx_Freeze build...")
        start_time = time.time()
        
        # Run the build
        result = subprocess.run([
            sys.executable, "setup_cx_freeze.py", "build"
        ], capture_output=True, text=True)
        
        build_time = time.time() - start_time
        
        if result.returncode == 0:
            print_success(f"Build completed in {build_time:.1f} seconds")
            print("Build output:")
            print(result.stdout[-500:])  # Show last 500 chars of output
            return True
        else:
            print_error("Build failed!")
            print("Error output:")
            print(result.stderr)
            print("Standard output:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print_error(f"Build process failed: {e}")
        return False

def verify_build():
    """Verify the build was successful"""
    print_step("5", "Verifying build")
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    build_dir = f"build/exe.win-amd64-{python_version}"
    exe_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
    
    if not os.path.exists(build_dir):
        print_error(f"Build directory not found: {build_dir}")
        return False
    
    if not os.path.exists(exe_path):
        print_error(f"Executable not found: {exe_path}")
        return False
    
    # Check file size
    exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print_success(f"Executable found: {exe_path}")
    print_success(f"Executable size: {exe_size:.1f} MB")
    
    # Check for key directories
    key_dirs = ["modules", "utils", "data", "lib"]
    for dir_name in key_dirs:
        dir_path = os.path.join(build_dir, dir_name)
        if os.path.exists(dir_path):
            print_success(f"Found directory: {dir_name}/")
        else:
            print_warning(f"Missing directory: {dir_name}/")
    
    print_success("Build verification completed")
    return True

def show_next_steps():
    """Show next steps after successful build"""
    print_header("BUILD COMPLETED SUCCESSFULLY!")
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    build_dir = f"build/exe.win-amd64-{python_version}"
    exe_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
    
    print(f"📦 Executable location: {exe_path}")
    print(f"📁 Build directory: {build_dir}")
    
    print("\n🚀 Next Steps:")
    print("1. Test the executable:")
    print(f'   cd "{build_dir}"')
    print("   VARSYS_Kitchen_Dashboard.exe")
    
    print("\n2. Create installer (optional):")
    print("   - Install Inno Setup")
    print("   - Run: VARSYS_Kitchen_Dashboard_Setup.iss")
    
    print("\n3. Distribution:")
    print("   - Test on clean Windows system")
    print("   - Create ZIP package for distribution")
    print("   - Upload to release platform")

def main():
    """Main build process"""
    print_header("VARSYS Kitchen Dashboard - Complete Build Process")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check required files
    if not check_required_files():
        return False
    
    # Clean previous builds
    clean_previous_builds()
    
    # Install dependencies
    if not install_dependencies():
        print_error("Dependency installation failed. Continuing anyway...")
    
    # Build executable
    if not build_executable():
        print_error("Build failed!")
        return False
    
    # Verify build
    if not verify_build():
        print_error("Build verification failed!")
        return False
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
