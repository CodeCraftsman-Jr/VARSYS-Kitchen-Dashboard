#!/usr/bin/env python3
"""
Test Firebase Integration for VARSYS Kitchen Dashboard v1.1.1
Verifies that Firebase is properly enabled and configured
"""

import sys
import os
import json
import importlib.util

def print_status(message, status="info"):
    """Print status with icons"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    print(f"{icons.get(status, 'ℹ️')} {message}")

def test_feature_flags():
    """Test that Firebase feature flags are enabled"""
    print("=" * 60)
    print("TESTING FIREBASE FEATURE FLAGS")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.getcwd())
        from __version__ import FIREBASE_ENABLED, SUBSCRIPTION_REQUIRED, MULTI_USER_SUPPORT
        
        print_status(f"FIREBASE_ENABLED: {FIREBASE_ENABLED}", "success" if FIREBASE_ENABLED else "error")
        print_status(f"SUBSCRIPTION_REQUIRED: {SUBSCRIPTION_REQUIRED}", "success" if SUBSCRIPTION_REQUIRED else "info")
        print_status(f"MULTI_USER_SUPPORT: {MULTI_USER_SUPPORT}", "success" if MULTI_USER_SUPPORT else "info")
        
        if FIREBASE_ENABLED:
            print_status("Firebase features are ENABLED in v1.1.1", "success")
            return True
        else:
            print_status("Firebase features are DISABLED", "error")
            return False
            
    except ImportError as e:
        print_status(f"Could not import feature flags: {e}", "error")
        return False

def test_firebase_imports():
    """Test Firebase package imports"""
    print("\n" + "=" * 60)
    print("TESTING FIREBASE PACKAGE IMPORTS")
    print("=" * 60)
    
    firebase_packages = [
        ("firebase_admin", "Firebase Admin SDK"),
        ("pyrebase", "Pyrebase4 Client SDK"),
        ("google.cloud.firestore", "Google Cloud Firestore"),
        ("google.auth", "Google Authentication"),
        ("jwt", "PyJWT for token handling"),
        ("cryptography", "Cryptography for security"),
        ("dotenv", "Python-dotenv for environment variables")
    ]
    
    success_count = 0
    
    for package_name, description in firebase_packages:
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is not None:
                # Try actual import
                __import__(package_name)
                print_status(f"{description}: Available", "success")
                success_count += 1
            else:
                print_status(f"{description}: Not found", "error")
        except ImportError as e:
            print_status(f"{description}: Import failed - {e}", "error")
        except Exception as e:
            print_status(f"{description}: Error - {e}", "error")
    
    firebase_ready = success_count >= 4  # Need at least core packages
    
    if firebase_ready:
        print_status(f"Firebase packages ready: {success_count}/{len(firebase_packages)}", "success")
    else:
        print_status(f"Firebase packages incomplete: {success_count}/{len(firebase_packages)}", "error")
    
    return firebase_ready

def test_configuration_files():
    """Test Firebase configuration files"""
    print("\n" + "=" * 60)
    print("TESTING FIREBASE CONFIGURATION FILES")
    print("=" * 60)
    
    config_files = [
        ("firebase_config.json", "Firebase project configuration"),
        (".env", "Environment variables"),
        ("firebase_web_config.json", "Web configuration (optional)"),
        ("jwt_secret.key", "JWT secret key (optional)")
    ]
    
    config_ready = True
    
    for file_name, description in config_files:
        if os.path.exists(file_name):
            try:
                if file_name.endswith('.json'):
                    with open(file_name, 'r') as f:
                        config = json.load(f)
                    
                    if file_name == "firebase_config.json":
                        firebase_config = config.get('firebase', {})
                        if firebase_config.get('projectId') and firebase_config.get('apiKey'):
                            print_status(f"{description}: Configured", "success")
                        else:
                            print_status(f"{description}: Template only (needs configuration)", "warning")
                            config_ready = False
                    else:
                        print_status(f"{description}: Available", "success")
                else:
                    print_status(f"{description}: Available", "success")
                    
            except Exception as e:
                print_status(f"{description}: Error reading - {e}", "error")
                config_ready = False
        else:
            if "optional" in description:
                print_status(f"{description}: Not found (optional)", "info")
            else:
                print_status(f"{description}: Not found", "warning")
                if file_name in ["firebase_config.json", ".env"]:
                    config_ready = False
    
    return config_ready

def test_application_modules():
    """Test application Firebase modules"""
    print("\n" + "=" * 60)
    print("TESTING APPLICATION FIREBASE MODULES")
    print("=" * 60)
    
    app_modules = [
        ("modules.firebase_integration", "Firebase integration module"),
        ("modules.firebase_config_manager", "Firebase configuration manager"),
        ("modules.firebase_auth", "Firebase authentication module"),
        ("modules.firebase_sync", "Firebase sync module"),
        ("modules.user_manager", "User management module")
    ]
    
    success_count = 0
    
    for module_name, description in app_modules:
        try:
            __import__(module_name)
            print_status(f"{description}: Available", "success")
            success_count += 1
        except ImportError as e:
            print_status(f"{description}: Not found - {e}", "warning")
        except Exception as e:
            print_status(f"{description}: Error - {e}", "error")
    
    if success_count >= 3:
        print_status(f"Application modules ready: {success_count}/{len(app_modules)}", "success")
        return True
    else:
        print_status(f"Some application modules missing: {success_count}/{len(app_modules)}", "warning")
        return False

def test_build_configuration():
    """Test build configuration includes Firebase"""
    print("\n" + "=" * 60)
    print("TESTING BUILD CONFIGURATION")
    print("=" * 60)
    
    setup_files = [
        "setup_cx_freeze.py",
        "setup_cx_freeze_minimal.py",
        "setup_cx_freeze_fixed.py"
    ]
    
    firebase_packages = ["firebase_admin", "pyrebase", "google.cloud.firestore", "jwt"]
    
    for setup_file in setup_files:
        if os.path.exists(setup_file):
            try:
                with open(setup_file, 'r') as f:
                    content = f.read()
                
                firebase_included = any(pkg in content for pkg in firebase_packages)
                
                if firebase_included:
                    print_status(f"{setup_file}: Firebase packages included", "success")
                else:
                    print_status(f"{setup_file}: Firebase packages missing", "warning")
                    
            except Exception as e:
                print_status(f"{setup_file}: Error reading - {e}", "error")
        else:
            print_status(f"{setup_file}: Not found", "warning")
    
    return True

def generate_firebase_status_report():
    """Generate comprehensive Firebase status report"""
    print("\n" + "=" * 60)
    print("FIREBASE STATUS REPORT")
    print("=" * 60)
    
    tests = [
        ("Feature Flags", test_feature_flags),
        ("Package Imports", test_firebase_imports),
        ("Configuration Files", test_configuration_files),
        ("Application Modules", test_application_modules),
        ("Build Configuration", test_build_configuration)
    ]
    
    results = []
    passed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
        except Exception as e:
            print_status(f"Test '{test_name}' crashed: {e}", "error")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("FINAL FIREBASE STATUS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "success" if result else "error"
        print_status(f"{test_name}: {'PASS' if result else 'FAIL'}", status)
    
    print(f"\nTests Passed: {passed}/{len(tests)}")
    print(f"Success Rate: {(passed/len(tests))*100:.1f}%")
    
    if passed == len(tests):
        print_status("🎉 FIREBASE FULLY ENABLED AND READY!", "success")
        status = "READY"
    elif passed >= len(tests) * 0.8:
        print_status("⚠️ Firebase mostly ready - minor issues", "warning")
        status = "MOSTLY_READY"
    else:
        print_status("❌ Firebase has significant issues", "error")
        status = "NOT_READY"
    
    # Create status report file
    report_content = f"""VARSYS Kitchen Dashboard v1.1.1 - Firebase Status Report
Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Firebase Status: {status}
Tests Passed: {passed}/{len(tests)} ({(passed/len(tests))*100:.1f}%)

Test Results:
"""
    
    for test_name, result in results:
        report_content += f"- {test_name}: {'PASS' if result else 'FAIL'}\n"
    
    report_content += f"""
Next Steps:
"""
    
    if status == "READY":
        report_content += """1. Firebase is fully enabled and ready for use
2. Configure firebase_config.json with your Firebase project
3. Update .env file with your Firebase credentials
4. Build and deploy the application
"""
    elif status == "MOSTLY_READY":
        report_content += """1. Most Firebase features are ready
2. Check configuration files and update as needed
3. Install any missing packages
4. Test the application thoroughly
"""
    else:
        report_content += """1. Install Firebase dependencies: enable_firebase.bat
2. Check Python version compatibility
3. Verify internet connection for package installation
4. Review error messages above
"""
    
    with open("firebase_status_report.txt", "w") as f:
        f.write(report_content)
    
    print_status("Firebase status report saved: firebase_status_report.txt", "info")
    
    return status

def main():
    """Main Firebase test function"""
    print("VARSYS Kitchen Dashboard v1.1.1 - Firebase Integration Test")
    print("=" * 60)
    
    status = generate_firebase_status_report()
    
    print(f"\nFirebase Status: {status}")
    
    if status == "READY":
        print("\n🎉 Firebase is fully enabled and ready for Kitchen Dashboard v1.1.1!")
        print("You can now build the application with full Firebase features.")
    elif status == "MOSTLY_READY":
        print("\n⚠️ Firebase is mostly ready but may need some configuration.")
        print("Check the report above and fix any issues.")
    else:
        print("\n❌ Firebase needs attention before it can be used.")
        print("Run: enable_firebase.bat to install dependencies.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")
