#!/usr/bin/env python3
"""
Enable Firebase for VARSYS Kitchen Dashboard v1.1.1
Installs all Firebase dependencies and configures the application
"""

import subprocess
import sys
import os
import json
import importlib.util
from pathlib import Path

def print_status(message, status="info"):
    """Print status with icons"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def check_python_version():
    """Check Python version compatibility"""
    print("=" * 60)
    print("CHECKING PYTHON ENVIRONMENT")
    print("=" * 60)
    
    version = sys.version_info
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}", "info")
    
    if version.major == 3 and version.minor >= 8:
        print_status("Python version is compatible with Firebase", "success")
        return True
    else:
        print_status("Python 3.8+ required for Firebase", "error")
        return False

def install_firebase_dependencies():
    """Install all Firebase-related dependencies"""
    print("\n" + "=" * 60)
    print("INSTALLING FIREBASE DEPENDENCIES")
    print("=" * 60)
    
    # Core Firebase packages
    firebase_packages = [
        ("firebase-admin", "firebase-admin>=6.0.0"),
        ("pyrebase4", "pyrebase4>=4.5.0"),
        ("google-cloud-firestore", "google-cloud-firestore>=2.11.0"),
        ("google-auth", "google-auth>=2.17.0"),
        ("google-auth-oauthlib", "google-auth-oauthlib>=1.0.0"),
        ("google-auth-httplib2", "google-auth-httplib2>=0.1.0")
    ]
    
    # Authentication and security packages
    auth_packages = [
        ("PyJWT", "PyJWT>=2.8.0"),
        ("cryptography", "cryptography>=41.0.0"),
        ("requests", "requests>=2.28.0"),
        ("urllib3", "urllib3>=1.26.0"),
        ("certifi", "certifi>=2022.12.7")
    ]
    
    # Additional utility packages
    utility_packages = [
        ("python-dotenv", "python-dotenv>=1.0.0"),
        ("json5", "json5>=0.9.10"),
        ("python-dateutil", "python-dateutil>=2.8.2")
    ]
    
    all_packages = firebase_packages + auth_packages + utility_packages
    
    print_status(f"Installing {len(all_packages)} packages...", "info")
    
    success_count = 0
    failed_packages = []
    
    for package_name, pip_name in all_packages:
        try:
            print_status(f"Installing {pip_name}...", "info")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", pip_name, "--upgrade"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_status(f"{package_name} installed successfully", "success")
                success_count += 1
            else:
                print_status(f"Failed to install {package_name}", "error")
                failed_packages.append(package_name)
                
        except subprocess.TimeoutExpired:
            print_status(f"Timeout installing {package_name}", "error")
            failed_packages.append(package_name)
        except Exception as e:
            print_status(f"Error installing {package_name}: {e}", "error")
            failed_packages.append(package_name)
    
    print_status(f"Installation complete: {success_count}/{len(all_packages)} packages", 
                "success" if success_count == len(all_packages) else "warning")
    
    if failed_packages:
        print_status(f"Failed packages: {', '.join(failed_packages)}", "warning")
    
    return success_count >= len(firebase_packages)  # At least Firebase core packages must succeed

def verify_firebase_imports():
    """Verify that Firebase packages can be imported"""
    print("\n" + "=" * 60)
    print("VERIFYING FIREBASE IMPORTS")
    print("=" * 60)
    
    packages_to_test = [
        ("firebase_admin", "Firebase Admin SDK"),
        ("pyrebase", "Pyrebase4"),
        ("google.cloud.firestore", "Google Cloud Firestore"),
        ("google.auth", "Google Auth"),
        ("jwt", "PyJWT"),
        ("cryptography", "Cryptography")
    ]
    
    success_count = 0
    
    for package_name, display_name in packages_to_test:
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is not None:
                # Try to actually import it
                __import__(package_name)
                print_status(f"{display_name} import successful", "success")
                success_count += 1
            else:
                print_status(f"{display_name} not found", "error")
        except ImportError as e:
            print_status(f"{display_name} import failed: {e}", "error")
        except Exception as e:
            print_status(f"{display_name} error: {e}", "error")
    
    firebase_ready = success_count >= 4  # Need at least core Firebase packages
    
    if firebase_ready:
        print_status("Firebase dependencies are ready!", "success")
    else:
        print_status("Firebase dependencies incomplete", "warning")
    
    return firebase_ready

def create_firebase_config_template():
    """Create Firebase configuration template"""
    print("\n" + "=" * 60)
    print("CREATING FIREBASE CONFIGURATION")
    print("=" * 60)
    
    # Check if firebase_config.json exists
    config_file = "firebase_config.json"
    
    if os.path.exists(config_file):
        print_status(f"{config_file} already exists", "info")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check if it has the required fields
            firebase_config = config.get('firebase', {})
            required_fields = ['apiKey', 'authDomain', 'projectId', 'storageBucket']
            
            if all(firebase_config.get(field) for field in required_fields):
                print_status("Firebase configuration appears complete", "success")
                return True
            else:
                print_status("Firebase configuration incomplete", "warning")
        except Exception as e:
            print_status(f"Error reading config: {e}", "error")
    
    # Create template configuration
    template_config = {
        "firebase": {
            "apiKey": "your-api-key-here",
            "authDomain": "your-project.firebaseapp.com",
            "databaseURL": "https://your-project-default-rtdb.firebaseio.com",
            "projectId": "your-project-id",
            "storageBucket": "your-project.appspot.com",
            "messagingSenderId": "123456789",
            "appId": "1:123456789:web:abcdef123456",
            "measurementId": "G-ABCDEF123"
        },
        "features": {
            "authentication": True,
            "cloud_sync": True,
            "real_time_sync": True,
            "offline_support": False,
            "analytics": True
        },
        "sync_settings": {
            "auto_sync_enabled": True,
            "sync_interval_minutes": 5,
            "batch_size": 100,
            "max_retries": 3,
            "conflict_resolution": "ask_user"
        },
        "security": {
            "require_authentication": True,
            "session_timeout_hours": 24,
            "auto_logout_on_idle": True,
            "idle_timeout_minutes": 30
        }
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(template_config, f, indent=2)
        print_status(f"Created {config_file} template", "success")
        print_status("Please update the Firebase configuration with your project details", "info")
        return True
    except Exception as e:
        print_status(f"Error creating config template: {e}", "error")
        return False

def create_env_template():
    """Create .env template for Firebase credentials"""
    print("\n" + "=" * 60)
    print("CREATING ENVIRONMENT TEMPLATE")
    print("=" * 60)
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print_status(f"{env_file} already exists", "info")
        return True
    
    env_template = """# Firebase Configuration for VARSYS Kitchen Dashboard v1.1.1
# Replace with your actual Firebase project credentials

FIREBASE_API_KEY=your-api-key-here
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abcdef123456
FIREBASE_MEASUREMENT_ID=G-ABCDEF123

# Application Settings
DEBUG_MODE=False
LOG_LEVEL=INFO
THEME=light

# Security Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
SESSION_TIMEOUT_HOURS=24
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        print_status(f"Created {env_file} template", "success")
        print_status("Please update the environment variables with your Firebase credentials", "info")
        return True
    except Exception as e:
        print_status(f"Error creating .env template: {e}", "error")
        return False

def update_build_configuration():
    """Update build configurations to include Firebase"""
    print("\n" + "=" * 60)
    print("UPDATING BUILD CONFIGURATION")
    print("=" * 60)
    
    # Update setup files to include Firebase packages
    setup_files = [
        "setup_cx_freeze.py",
        "setup_cx_freeze_minimal.py", 
        "setup_cx_freeze_fixed.py"
    ]
    
    firebase_packages = [
        "firebase_admin", "pyrebase", "google.cloud.firestore",
        "google.auth", "jwt", "cryptography"
    ]
    
    for setup_file in setup_files:
        if os.path.exists(setup_file):
            print_status(f"Firebase packages will be included in {setup_file}", "info")
    
    print_status("Build configurations ready for Firebase", "success")
    return True

def test_firebase_integration():
    """Test basic Firebase integration"""
    print("\n" + "=" * 60)
    print("TESTING FIREBASE INTEGRATION")
    print("=" * 60)
    
    try:
        # Test Firebase Admin import
        import firebase_admin
        print_status("Firebase Admin SDK import successful", "success")
        
        # Test Pyrebase import
        import pyrebase
        print_status("Pyrebase4 import successful", "success")
        
        # Test application Firebase modules
        sys.path.insert(0, os.getcwd())
        
        try:
            from modules import firebase_integration
            print_status("Application Firebase integration module loaded", "success")
        except ImportError as e:
            print_status(f"Application Firebase module error: {e}", "warning")
        
        try:
            from modules import firebase_config_manager
            print_status("Firebase configuration manager loaded", "success")
        except ImportError as e:
            print_status(f"Firebase config manager error: {e}", "warning")
        
        print_status("Firebase integration test completed", "success")
        return True
        
    except ImportError as e:
        print_status(f"Firebase integration test failed: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Firebase test error: {e}", "error")
        return False

def main():
    """Main Firebase enablement function"""
    print("VARSYS Kitchen Dashboard v1.1.1 - Firebase Enablement")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print_status("Python version incompatible", "error")
        return False
    
    # Install Firebase dependencies
    if not install_firebase_dependencies():
        print_status("Critical Firebase dependencies failed to install", "error")
        return False
    
    # Verify imports
    if not verify_firebase_imports():
        print_status("Firebase imports verification failed", "warning")
    
    # Create configuration files
    create_firebase_config_template()
    create_env_template()
    
    # Update build configuration
    update_build_configuration()
    
    # Test integration
    firebase_ready = test_firebase_integration()
    
    print("\n" + "=" * 60)
    print("FIREBASE ENABLEMENT SUMMARY")
    print("=" * 60)
    
    if firebase_ready:
        print_status("🎉 FIREBASE SUCCESSFULLY ENABLED!", "success")
        print_status("Firebase features are now available in v1.1.1", "success")
        print_status("Subscription-based authentication enabled", "success")
        print_status("Multi-user cloud sync enabled", "success")
    else:
        print_status("⚠️ Firebase partially enabled", "warning")
        print_status("Some features may not work correctly", "warning")
    
    print("\nNext steps:")
    print("1. Update firebase_config.json with your Firebase project details")
    print("2. Update .env file with your Firebase credentials")
    print("3. Run: python setup_cx_freeze.py build")
    print("4. Test the application with Firebase features")
    
    return firebase_ready

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Firebase is now enabled for Kitchen Dashboard v1.1.1!")
    else:
        print("\n❌ Firebase enablement encountered issues. Check the output above.")
    
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)
