#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Build Script with Firebase Support
Ensures all Firebase dependencies are properly included
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
    print(f"\nStep {step_num}: {description}")

def print_success(message):
    """Print a success message"""
    print(f"SUCCESS: {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"WARNING: {message}")

def print_error(message):
    """Print an error message"""
    print(f"ERROR: {message}")

def check_firebase_dependencies():
    """Check if Firebase dependencies are installed"""
    print_step("1", "Checking Firebase dependencies")
    
    firebase_packages = [
        "firebase-admin",
        "pyrebase4", 
        "PyJWT",
        "cryptography",
        "google-auth",
        "google-cloud-firestore"
    ]
    
    missing_packages = []
    
    for package in firebase_packages:
        try:
            if package == "firebase-admin":
                import firebase_admin
                print_success(f"firebase-admin: {firebase_admin.__version__}")
            elif package == "pyrebase4":
                import pyrebase
                print_success("pyrebase4: Available")
            elif package == "PyJWT":
                import jwt
                print_success(f"PyJWT: {jwt.__version__}")
            elif package == "cryptography":
                import cryptography
                print_success(f"cryptography: {cryptography.__version__}")
            elif package == "google-auth":
                import google.auth
                print_success("google-auth: Available")
            elif package == "google-cloud-firestore":
                try:
                    import google.cloud.firestore
                    print_success("google-cloud-firestore: Available")
                except ImportError:
                    print_warning("google-cloud-firestore: Not available (optional)")
        except ImportError:
            print_error(f"{package}: Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing Firebase packages: {missing_packages}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True)
                print_success(f"Installed {package}")
            except subprocess.CalledProcessError:
                print_error(f"Failed to install {package}")
    
    return len(missing_packages) == 0

def clean_build():
    """Clean previous build"""
    print_step("2", "Cleaning previous build")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
        print_success("Removed build directory")
    else:
        print("No previous build found")

def build_with_firebase():
    """Build executable with Firebase support"""
    print_step("3", "Building executable with Firebase support")
    
    try:
        start_time = time.time()
        
        # Run the enhanced build
        result = subprocess.run([
            sys.executable, "setup_cx_freeze.py", "build"
        ], capture_output=True, text=True)
        
        build_time = time.time() - start_time
        
        if result.returncode == 0:
            print_success(f"Build completed in {build_time:.1f} seconds")
            return True
        else:
            print_error("Build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Build process failed: {e}")
        return False

def verify_firebase_in_build():
    """Verify Firebase modules are included in build"""
    print_step("4", "Verifying Firebase modules in build")
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    build_dir = f"build/exe.win-amd64-{python_version}"
    lib_dir = os.path.join(build_dir, "lib")
    
    if not os.path.exists(lib_dir):
        print_error(f"Build lib directory not found: {lib_dir}")
        return False
    
    # Check for Firebase modules
    firebase_modules = [
        "firebase_admin",
        "pyrebase", 
        "jwt",
        "cryptography",
        "google"
    ]
    
    found_modules = []
    missing_modules = []
    
    for module in firebase_modules:
        module_path = os.path.join(lib_dir, module)
        if os.path.exists(module_path):
            found_modules.append(module)
            print_success(f"Found: {module}")
        else:
            missing_modules.append(module)
            print_warning(f"Missing: {module}")
    
    print(f"\nFirebase modules found: {len(found_modules)}/{len(firebase_modules)}")
    
    if missing_modules:
        print_warning(f"Missing modules: {missing_modules}")
        print("The application may not work properly on other PCs")
        return False
    else:
        print_success("All Firebase modules included!")
        return True

def create_firebase_test():
    """Create a test script to verify Firebase works in the build"""
    print_step("5", "Creating Firebase test script")
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    build_dir = f"build/exe.win-amd64-{python_version}"
    
    test_script = f"""
import sys
import os

# Test Firebase imports
try:
    import firebase_admin
    print("SUCCESS: firebase_admin imported")
except ImportError as e:
    print(f"ERROR: firebase_admin import failed: {{e}}")

try:
    import pyrebase
    print("SUCCESS: pyrebase imported")
except ImportError as e:
    print(f"ERROR: pyrebase import failed: {{e}}")

try:
    import jwt
    print("SUCCESS: jwt imported")
except ImportError as e:
    print(f"ERROR: jwt import failed: {{e}}")

try:
    import cryptography
    print("SUCCESS: cryptography imported")
except ImportError as e:
    print(f"ERROR: cryptography import failed: {{e}}")

print("Firebase test completed")
input("Press Enter to exit...")
"""
    
    test_file = os.path.join(build_dir, "test_firebase.py")
    try:
        with open(test_file, 'w') as f:
            f.write(test_script)
        print_success(f"Created test script: {test_file}")
        return True
    except Exception as e:
        print_error(f"Failed to create test script: {e}")
        return False

def show_results():
    """Show build results and next steps"""
    print_header("BUILD COMPLETED WITH FIREBASE SUPPORT!")
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    build_dir = f"build/exe.win-amd64-{python_version}"
    exe_path = os.path.join(build_dir, "VARSYS_Kitchen_Dashboard.exe")
    
    print(f"Executable: {exe_path}")
    print(f"Build directory: {build_dir}")
    
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"Executable size: {exe_size:.1f} MB")
    
    print("\nNext Steps:")
    print("1. Test the executable on this PC:")
    print(f'   cd "{build_dir}"')
    print("   VARSYS_Kitchen_Dashboard.exe")
    
    print("\n2. Test Firebase functionality:")
    print(f'   cd "{build_dir}"')
    print("   python test_firebase.py")
    
    print("\n3. Test on another PC:")
    print("   - Copy the entire build directory to another PC")
    print("   - Run VARSYS_Kitchen_Dashboard.exe")
    print("   - Verify Firebase authentication works")
    
    print("\n4. Create installer:")
    print("   - Use Inno Setup with VARSYS_Kitchen_Dashboard_Setup.iss")
    print("   - Test installer on clean Windows system")

def main():
    """Main build process with Firebase support"""
    print_header("VARSYS Kitchen Dashboard - Firebase-Enabled Build")
    
    # Check Firebase dependencies
    if not check_firebase_dependencies():
        print_error("Firebase dependencies check failed!")
        return False
    
    # Clean previous build
    clean_build()
    
    # Build with Firebase
    if not build_with_firebase():
        print_error("Build failed!")
        return False
    
    # Verify Firebase modules
    firebase_ok = verify_firebase_in_build()
    
    # Create test script
    create_firebase_test()
    
    # Show results
    show_results()
    
    if firebase_ok:
        print_success("Build completed successfully with Firebase support!")
    else:
        print_warning("Build completed but some Firebase modules may be missing")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
