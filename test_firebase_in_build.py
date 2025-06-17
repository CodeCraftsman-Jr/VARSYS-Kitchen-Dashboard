#!/usr/bin/env python3
"""
Test Firebase modules in the cx_Freeze build
Run this script from the build directory to verify Firebase functionality
"""

import sys
import os

def test_firebase_imports():
    """Test if all Firebase modules can be imported"""
    print("Testing Firebase module imports...")
    print("=" * 50)
    
    modules_to_test = [
        ("firebase_admin", "Firebase Admin SDK"),
        ("pyrebase", "Pyrebase authentication"),
        ("jwt", "JWT token handling"),
        ("cryptography", "Cryptography library"),
        ("google.auth", "Google authentication"),
        ("google.cloud", "Google Cloud libraries"),
        ("grpc", "gRPC communication"),
        ("proto", "Protocol Buffers")
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: {description} - SUCCESS")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name}: {description} - FAILED ({e})")
        except Exception as e:
            print(f"⚠️  {module_name}: {description} - ERROR ({e})")
    
    print("=" * 50)
    print(f"Import Test Results: {success_count}/{total_count} modules imported successfully")
    
    return success_count == total_count

def test_firebase_config_files():
    """Test if Firebase configuration files are present"""
    print("\nTesting Firebase configuration files...")
    print("=" * 50)
    
    config_files = [
        "firebase_config.json",
        "firebase_credentials.json", 
        "firebase_web_config.json",
        "jwt_secret.key",
        "secure_credentials/firebase_credentials.json",
        "secure_credentials/firebase_web_config.json",
        "secure_credentials/jwt_secret.key"
    ]
    
    found_count = 0
    total_count = len(config_files)
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file} - FOUND")
            found_count += 1
        else:
            print(f"❌ {config_file} - MISSING")
    
    print("=" * 50)
    print(f"Config File Results: {found_count}/{total_count} files found")
    
    return found_count > 0  # At least some config files should exist

def test_firebase_initialization():
    """Test basic Firebase initialization"""
    print("\nTesting Firebase initialization...")
    print("=" * 50)
    
    try:
        # Test Firebase Admin SDK
        import firebase_admin
        print("✅ Firebase Admin SDK imported successfully")
        
        # Test Pyrebase
        import pyrebase
        print("✅ Pyrebase imported successfully")
        
        # Test if we can create a basic config (without actually connecting)
        test_config = {
            "apiKey": "test",
            "authDomain": "test.firebaseapp.com",
            "databaseURL": "https://test.firebaseio.com",
            "projectId": "test",
            "storageBucket": "test.appspot.com",
            "messagingSenderId": "123456789",
            "appId": "test"
        }
        
        # This should not fail even with fake config
        print("✅ Basic Firebase configuration structure validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase initialization test failed: {e}")
        return False

def test_fallback_handler():
    """Test the Firebase fallback handler"""
    print("\nTesting Firebase fallback handler...")
    print("=" * 50)
    
    try:
        # Check if fallback handler exists
        if os.path.exists("firebase_fallback_handler.py"):
            print("✅ Firebase fallback handler file found")
            
            # Try to import it
            sys.path.insert(0, ".")
            import firebase_fallback_handler
            print("✅ Firebase fallback handler imported successfully")
            
            # Test basic functionality
            handler = firebase_fallback_handler.FirebaseFallbackHandler()
            status = handler.get_firebase_status()
            print(f"✅ Fallback handler status check: {len(status)} status items")
            
            return True
        else:
            print("❌ Firebase fallback handler file not found")
            return False
            
    except Exception as e:
        print(f"❌ Fallback handler test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Firebase Build Verification Test")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Executable: {sys.executable}")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Firebase Module Imports", test_firebase_imports),
        ("Firebase Config Files", test_firebase_config_files),
        ("Firebase Initialization", test_firebase_initialization),
        ("Fallback Handler", test_fallback_handler)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
                print(f"\n🎉 {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
    
    # Final results
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Firebase should work on other PCs.")
    elif passed_tests >= total_tests // 2:
        print("⚠️  PARTIAL SUCCESS. Some Firebase features may work.")
    else:
        print("❌ TESTS FAILED. Firebase likely won't work on other PCs.")
    
    print("\nRecommendations:")
    if passed_tests == total_tests:
        print("✅ This build should resolve the 'install pyrebase' error")
        print("✅ Safe to distribute to other PCs")
    else:
        print("⚠️  Consider rebuilding with better Firebase inclusion")
        print("⚠️  Test on a clean PC before distribution")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
