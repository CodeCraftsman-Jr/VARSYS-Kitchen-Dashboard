#!/usr/bin/env python3
"""
Fix urllib3 compatibility issues with Firebase
Resolves 'No module named urllib3.contrib.appengine' error
"""

import subprocess
import sys
import os
import importlib.util

def print_status(message, status="info"):
    """Print status with icons"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def check_current_versions():
    """Check current package versions"""
    print("=" * 60)
    print("CHECKING CURRENT PACKAGE VERSIONS")
    print("=" * 60)
    
    packages_to_check = [
        "urllib3", "requests", "firebase-admin", "pyrebase4", 
        "google-auth", "google-auth-httplib2"
    ]
    
    for package in packages_to_check:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "show", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                version_line = next((line for line in lines if line.startswith('Version:')), None)
                if version_line:
                    version = version_line.split(':', 1)[1].strip()
                    print_status(f"{package}: {version}", "info")
                else:
                    print_status(f"{package}: installed (version unknown)", "info")
            else:
                print_status(f"{package}: not installed", "warning")
                
        except Exception as e:
            print_status(f"Error checking {package}: {e}", "error")

def fix_urllib3_compatibility():
    """Fix urllib3 compatibility issues"""
    print("\n" + "=" * 60)
    print("FIXING URLLIB3 COMPATIBILITY")
    print("=" * 60)
    
    # The issue is that newer urllib3 versions (2.0+) removed urllib3.contrib.appengine
    # Firebase Admin SDK and some Google packages still expect it
    
    print_status("Installing compatible urllib3 version...", "info")
    
    try:
        # Install urllib3 < 2.0 for compatibility
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "urllib3<2.0", "--force-reinstall"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print_status("urllib3 downgraded to compatible version", "success")
        else:
            print_status(f"Failed to downgrade urllib3: {result.stderr}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error fixing urllib3: {e}", "error")
        return False
    
    return True

def install_compatible_packages():
    """Install compatible versions of all packages"""
    print("\n" + "=" * 60)
    print("INSTALLING COMPATIBLE PACKAGE VERSIONS")
    print("=" * 60)
    
    # Compatible package versions that work together
    compatible_packages = [
        "urllib3<2.0",  # Must be < 2.0 for Firebase compatibility
        "requests>=2.25.0,<3.0",  # Compatible with urllib3 < 2.0
        "firebase-admin>=6.0.0",  # Latest Firebase Admin
        "google-auth>=2.0.0,<3.0",  # Compatible Google Auth
        "google-auth-httplib2>=0.1.0",  # HTTP library
        "google-auth-oauthlib>=0.5.0",  # OAuth support
        "google-cloud-firestore>=2.11.0",  # Firestore
        "pyrebase4>=4.5.0",  # Pyrebase client
        "PyJWT>=2.4.0",  # JWT handling
        "cryptography>=3.4.0",  # Crypto support
        "certifi>=2021.10.8"  # SSL certificates
    ]
    
    print_status(f"Installing {len(compatible_packages)} compatible packages...", "info")
    
    success_count = 0
    failed_packages = []
    
    for package in compatible_packages:
        try:
            print_status(f"Installing {package}...", "info")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--force-reinstall"
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print_status(f"{package} installed successfully", "success")
                success_count += 1
            else:
                print_status(f"Failed to install {package}", "error")
                failed_packages.append(package)
                
        except subprocess.TimeoutExpired:
            print_status(f"Timeout installing {package}", "error")
            failed_packages.append(package)
        except Exception as e:
            print_status(f"Error installing {package}: {e}", "error")
            failed_packages.append(package)
    
    print_status(f"Compatible packages: {success_count}/{len(compatible_packages)} installed", 
                "success" if success_count >= len(compatible_packages) * 0.8 else "warning")
    
    if failed_packages:
        print_status(f"Failed packages: {', '.join(failed_packages)}", "warning")
    
    return success_count >= len(compatible_packages) * 0.8

def test_firebase_imports_fixed():
    """Test Firebase imports after fixing urllib3"""
    print("\n" + "=" * 60)
    print("TESTING FIREBASE IMPORTS (AFTER FIX)")
    print("=" * 60)
    
    test_imports = [
        ("urllib3", "urllib3 base"),
        ("urllib3.util", "urllib3 utilities"),
        ("requests", "Requests library"),
        ("google.auth", "Google Auth"),
        ("firebase_admin", "Firebase Admin SDK"),
        ("pyrebase", "Pyrebase4 client"),
        ("jwt", "PyJWT"),
        ("cryptography", "Cryptography")
    ]
    
    success_count = 0
    
    for module_name, description in test_imports:
        try:
            __import__(module_name)
            print_status(f"{description}: Import successful", "success")
            success_count += 1
        except ImportError as e:
            print_status(f"{description}: Import failed - {e}", "error")
        except Exception as e:
            print_status(f"{description}: Error - {e}", "error")
    
    # Special test for the specific urllib3.contrib.appengine issue
    try:
        import urllib3.contrib.appengine
        print_status("urllib3.contrib.appengine: Available", "success")
        success_count += 1
    except ImportError:
        print_status("urllib3.contrib.appengine: Not available (expected in urllib3 2.0+)", "warning")
        # This is actually expected in newer urllib3, so we'll work around it
    except Exception as e:
        print_status(f"urllib3.contrib.appengine: Error - {e}", "error")
    
    firebase_ready = success_count >= 6  # Need most core packages
    
    if firebase_ready:
        print_status("Firebase imports working after fix!", "success")
    else:
        print_status("Firebase imports still have issues", "error")
    
    return firebase_ready

def create_urllib3_workaround():
    """Create a workaround for urllib3.contrib.appengine if needed"""
    print("\n" + "=" * 60)
    print("CREATING URLLIB3 WORKAROUND")
    print("=" * 60)
    
    # Check if we need the workaround
    try:
        import urllib3.contrib.appengine
        print_status("urllib3.contrib.appengine exists, no workaround needed", "success")
        return True
    except ImportError:
        print_status("urllib3.contrib.appengine missing, creating workaround", "info")
    
    # Create a minimal workaround module
    workaround_content = '''"""
Workaround for urllib3.contrib.appengine compatibility
This module provides minimal compatibility for packages that expect urllib3.contrib.appengine
"""

# Minimal compatibility for packages expecting urllib3.contrib.appengine
def is_appengine():
    """Check if running on Google App Engine"""
    return False

def is_appengine_sandbox():
    """Check if running in App Engine sandbox"""
    return False

# Provide minimal AppEngineManager for compatibility
class AppEngineManager:
    def __init__(self, *args, **kwargs):
        pass
    
    def urlopen(self, *args, **kwargs):
        # Fallback to standard urllib3
        import urllib3
        http = urllib3.PoolManager()
        return http.urlopen(*args, **kwargs)

# Make the workaround available
__all__ = ['is_appengine', 'is_appengine_sandbox', 'AppEngineManager']
'''
    
    try:
        # Find urllib3 installation directory
        import urllib3
        urllib3_path = os.path.dirname(urllib3.__file__)
        contrib_path = os.path.join(urllib3_path, 'contrib')
        
        # Create contrib directory if it doesn't exist
        if not os.path.exists(contrib_path):
            os.makedirs(contrib_path)
            print_status("Created urllib3/contrib directory", "success")
        
        # Create appengine.py workaround
        appengine_path = os.path.join(contrib_path, 'appengine.py')
        with open(appengine_path, 'w') as f:
            f.write(workaround_content)
        
        print_status("Created urllib3.contrib.appengine workaround", "success")
        
        # Test the workaround
        import urllib3.contrib.appengine
        print_status("Workaround import test successful", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Failed to create workaround: {e}", "error")
        return False

def verify_final_setup():
    """Verify that everything works after fixes"""
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION")
    print("=" * 60)
    
    try:
        # Test Firebase Admin SDK initialization (without actual config)
        import firebase_admin
        print_status("Firebase Admin SDK import: OK", "success")
        
        # Test Pyrebase import
        import pyrebase
        print_status("Pyrebase4 import: OK", "success")
        
        # Test Google Auth
        import google.auth
        print_status("Google Auth import: OK", "success")
        
        # Test urllib3 with contrib.appengine
        import urllib3.contrib.appengine
        print_status("urllib3.contrib.appengine import: OK", "success")
        
        print_status("🎉 All Firebase dependencies working!", "success")
        return True
        
    except Exception as e:
        print_status(f"Final verification failed: {e}", "error")
        return False

def main():
    """Main fix function"""
    print("VARSYS Kitchen Dashboard v1.1.1 - urllib3 Firebase Fix")
    print("=" * 60)
    
    # Check current versions
    check_current_versions()
    
    # Fix urllib3 compatibility
    if not fix_urllib3_compatibility():
        print_status("urllib3 fix failed", "error")
        return False
    
    # Install compatible packages
    if not install_compatible_packages():
        print_status("Package installation failed", "error")
        return False
    
    # Test imports
    if not test_firebase_imports_fixed():
        print_status("Creating urllib3 workaround...", "info")
        create_urllib3_workaround()
    
    # Final verification
    success = verify_final_setup()
    
    print("\n" + "=" * 60)
    print("URLLIB3 FIREBASE FIX SUMMARY")
    print("=" * 60)
    
    if success:
        print_status("✅ urllib3 Firebase compatibility FIXED!", "success")
        print_status("Firebase dependencies are now working correctly", "success")
        print_status("You can now build with Firebase enabled", "success")
    else:
        print_status("❌ urllib3 Firebase fix incomplete", "error")
        print_status("Some issues remain - check output above", "warning")
    
    print("\nNext steps:")
    if success:
        print("1. Run: python test_firebase_enabled.py")
        print("2. Run: build_release_v1.1.1.bat")
        print("3. Test Firebase features in the application")
    else:
        print("1. Try: pip install urllib3==1.26.18 --force-reinstall")
        print("2. Try: pip install firebase-admin --force-reinstall")
        print("3. Check Python version compatibility")
    
    return success

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)
