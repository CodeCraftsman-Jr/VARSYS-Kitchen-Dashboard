#!/usr/bin/env python3
"""
Fix Build Dependencies for VARSYS Kitchen Dashboard v1.1.1
Installs missing dependencies and fixes common build issues
"""

import subprocess
import sys
import os
import importlib.util

def print_status(message, status="info"):
    """Print status with icons"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def check_python_version():
    """Check Python version compatibility"""
    print("=" * 50)
    print("CHECKING PYTHON ENVIRONMENT")
    print("=" * 50)
    
    version = sys.version_info
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}", "info")
    
    if version.major == 3 and version.minor in [12, 13]:
        print_status("Python version is compatible", "success")
        return True
    else:
        print_status("Python 3.12 or 3.13 required for optimal compatibility", "warning")
        return False

def install_package(package_name, pip_name=None):
    """Install a single package"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        # Check if package is already installed
        spec = importlib.util.find_spec(package_name)
        if spec is not None:
            print_status(f"{package_name} already installed", "success")
            return True
    except ImportError:
        pass
    
    try:
        print_status(f"Installing {pip_name}...", "info")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", pip_name, "--upgrade"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_status(f"{pip_name} installed successfully", "success")
            return True
        else:
            print_status(f"Failed to install {pip_name}: {result.stderr}", "error")
            return False
            
    except subprocess.TimeoutExpired:
        print_status(f"Timeout installing {pip_name}", "error")
        return False
    except Exception as e:
        print_status(f"Error installing {pip_name}: {e}", "error")
        return False

def install_core_dependencies():
    """Install core dependencies required for building"""
    print("\n" + "=" * 50)
    print("INSTALLING CORE DEPENDENCIES")
    print("=" * 50)
    
    core_packages = [
        ("cx_Freeze", "cx_Freeze>=6.15.0"),
        ("pandas", "pandas>=1.5.0"),
        ("matplotlib", "matplotlib>=3.5.0"),
        ("PySide6", "PySide6>=6.0.0"),
        ("numpy", "numpy>=1.22.0"),
        ("openpyxl", "openpyxl>=3.0.0"),
        ("PIL", "Pillow>=9.0.0"),
        ("requests", "requests>=2.28.0"),
        ("urllib3", "urllib3>=1.26.0"),
        ("certifi", "certifi>=2022.12.7")
    ]
    
    success_count = 0
    for package_name, pip_name in core_packages:
        if install_package(package_name, pip_name):
            success_count += 1
    
    print_status(f"Core dependencies: {success_count}/{len(core_packages)} installed", 
                "success" if success_count == len(core_packages) else "warning")
    return success_count == len(core_packages)

def install_firebase_dependencies():
    """Install Firebase dependencies (optional)"""
    print("\n" + "=" * 50)
    print("INSTALLING FIREBASE DEPENDENCIES")
    print("=" * 50)
    
    firebase_packages = [
        ("firebase_admin", "firebase-admin>=6.0.0"),
        ("pyrebase", "pyrebase4>=4.5.0")
    ]
    
    success_count = 0
    for package_name, pip_name in firebase_packages:
        if install_package(package_name, pip_name):
            success_count += 1
    
    if success_count == len(firebase_packages):
        print_status("Firebase dependencies installed successfully", "success")
        return True
    else:
        print_status("Some Firebase dependencies failed - continuing without them", "warning")
        return False

def install_optional_dependencies():
    """Install optional dependencies"""
    print("\n" + "=" * 50)
    print("INSTALLING OPTIONAL DEPENDENCIES")
    print("=" * 50)
    
    optional_packages = [
        ("seaborn", "seaborn>=0.12.0"),
        ("sklearn", "scikit-learn>=1.3.0"),
        ("jwt", "PyJWT>=2.8.0"),
        ("cryptography", "cryptography>=41.0.0"),
        ("tqdm", "tqdm>=4.64.0"),
        ("dateutil", "python-dateutil>=2.8.2"),
        ("dotenv", "python-dotenv>=1.0.0"),
        ("loguru", "loguru>=0.6.0"),
        ("json5", "json5>=0.9.10")
    ]
    
    success_count = 0
    for package_name, pip_name in optional_packages:
        if install_package(package_name, pip_name):
            success_count += 1
    
    print_status(f"Optional dependencies: {success_count}/{len(optional_packages)} installed", "info")
    return True

def install_windows_dependencies():
    """Install Windows-specific dependencies"""
    if sys.platform != "win32":
        return True
        
    print("\n" + "=" * 50)
    print("INSTALLING WINDOWS DEPENDENCIES")
    print("=" * 50)
    
    windows_packages = [
        ("win32api", "pywin32>=305"),
        ("win32con", "pywin32-ctypes>=0.2.0")
    ]
    
    success_count = 0
    for package_name, pip_name in windows_packages:
        if install_package(package_name, pip_name):
            success_count += 1
    
    print_status(f"Windows dependencies: {success_count}/{len(windows_packages)} installed", "info")
    return True

def update_pip():
    """Update pip to latest version"""
    print("\n" + "=" * 50)
    print("UPDATING PIP")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print_status("pip updated successfully", "success")
            return True
        else:
            print_status("pip update failed, continuing anyway", "warning")
            return False
    except Exception as e:
        print_status(f"Error updating pip: {e}", "warning")
        return False

def create_requirements_backup():
    """Create a working requirements.txt for the build"""
    print("\n" + "=" * 50)
    print("CREATING BUILD REQUIREMENTS")
    print("=" * 50)
    
    # Minimal requirements for building
    build_requirements = """# Build Requirements for VARSYS Kitchen Dashboard v1.1.1
# Core dependencies (required)
cx_Freeze>=6.15.0
pandas>=1.5.0
matplotlib>=3.5.0
PySide6>=6.0.0
numpy>=1.22.0
openpyxl>=3.0.0
Pillow>=9.0.0
requests>=2.28.0
urllib3>=1.26.0
certifi>=2022.12.7

# Firebase (optional - will be excluded if not available)
firebase-admin>=6.0.0
pyrebase4>=4.5.0

# Optional dependencies
seaborn>=0.12.0
scikit-learn>=1.3.0
PyJWT>=2.8.0
cryptography>=41.0.0
tqdm>=4.64.0
python-dateutil>=2.8.2
python-dotenv>=1.0.0
loguru>=0.6.0
json5>=0.9.10

# Windows-specific
pywin32>=305; sys_platform == "win32"
pywin32-ctypes>=0.2.0; sys_platform == "win32"
"""
    
    try:
        with open("requirements_build.txt", "w") as f:
            f.write(build_requirements)
        print_status("Build requirements file created", "success")
        return True
    except Exception as e:
        print_status(f"Error creating build requirements: {e}", "error")
        return False

def install_from_requirements():
    """Install from requirements.txt if it exists"""
    if os.path.exists("requirements.txt"):
        print("\n" + "=" * 50)
        print("INSTALLING FROM REQUIREMENTS.TXT")
        print("=" * 50)
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print_status("Requirements installed successfully", "success")
                return True
            else:
                print_status("Some requirements failed, continuing with manual installation", "warning")
                return False
        except Exception as e:
            print_status(f"Error installing requirements: {e}", "warning")
            return False
    return True

def main():
    """Main dependency installation function"""
    print("VARSYS Kitchen Dashboard v1.1.1 - Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Update pip first
    update_pip()
    
    # Try installing from requirements.txt first
    install_from_requirements()
    
    # Install dependencies in order of importance
    core_success = install_core_dependencies()
    firebase_success = install_firebase_dependencies()
    install_optional_dependencies()
    install_windows_dependencies()
    
    # Create backup requirements
    create_requirements_backup()
    
    print("\n" + "=" * 60)
    print("DEPENDENCY INSTALLATION SUMMARY")
    print("=" * 60)
    
    if core_success:
        print_status("✅ Core dependencies installed - BUILD SHOULD WORK", "success")
    else:
        print_status("❌ Core dependencies missing - BUILD WILL FAIL", "error")
    
    if firebase_success:
        print_status("✅ Firebase dependencies available", "success")
    else:
        print_status("⚠️ Firebase dependencies missing - will be excluded from build", "warning")
    
    print("\nNext steps:")
    print("1. Run: python setup_cx_freeze.py build")
    print("2. If build fails, run: python setup_cx_freeze_minimal.py build")
    print("3. Test the executable in the build directory")
    
    return core_success

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Critical dependencies missing. Please install manually:")
        print("pip install cx_Freeze pandas matplotlib PySide6 numpy")
        sys.exit(1)
    else:
        print("\n✅ Dependencies ready for building!")
        sys.exit(0)
