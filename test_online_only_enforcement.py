#!/usr/bin/env python3
"""
Test Online-Only Mode Enforcement for Kitchen Dashboard v1.0.6
This script tests that the application properly enforces online-only mode
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

def backup_firebase_config():
    """Backup current Firebase configuration"""
    backup_files = {}

    files_to_backup = [
        'firebase_config.json',
        'firebase_web_config.json',
        'secure_credentials/firebase_web_config.json'
    ]

    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = f"{file_path}.test_backup"
            # Create directory if needed
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            shutil.copy2(file_path, backup_path)
            backup_files[file_path] = backup_path
            print(f"📋 Backed up {file_path} to {backup_path}")

    return backup_files

def restore_firebase_config(backup_files):
    """Restore Firebase configuration from backup"""
    for original_path, backup_path in backup_files.items():
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, original_path)
            os.remove(backup_path)
            print(f"🔄 Restored {original_path} from backup")

def create_invalid_firebase_config():
    """Create invalid Firebase configuration for testing"""
    invalid_config = {
        "firebase": {
            "apiKey": "",
            "authDomain": "",
            "databaseURL": "",
            "projectId": "",
            "storageBucket": "",
            "messagingSenderId": "",
            "appId": "",
            "measurementId": ""
        },
        "features": {
            "authentication": True,
            "cloud_sync": True,
            "real_time_sync": True,
            "offline_support": False,
            "analytics": True
        },
        "security": {
            "require_authentication": True,
            "session_timeout_hours": 24,
            "auto_logout_on_idle": True,
            "idle_timeout_minutes": 30
        }
    }
    
    with open('firebase_config.json', 'w') as f:
        json.dump(invalid_config, f, indent=2)
    
    print("❌ Created invalid Firebase configuration")

def remove_firebase_config():
    """Remove Firebase configuration files"""
    files_to_remove = [
        'firebase_config.json',
        'firebase_web_config.json',
        'secure_credentials/firebase_web_config.json'
    ]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removed {file_path}")

def test_no_firebase_config():
    """Test application behavior with no Firebase configuration"""
    print("\n🧪 Test 1: No Firebase Configuration")
    print("-" * 50)
    
    # Remove Firebase config files
    remove_firebase_config()
    
    # Try to import and check Firebase config manager
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        
        config_manager = get_firebase_config_manager()
        
        if config_manager.is_configured():
            print("❌ FAIL: Config manager reports Firebase as configured when it shouldn't be")
            return False
        else:
            print("✅ PASS: Config manager correctly reports Firebase as not configured")
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Error testing config manager: {e}")
        return False

def test_invalid_firebase_config():
    """Test application behavior with invalid Firebase configuration"""
    print("\n🧪 Test 2: Invalid Firebase Configuration")
    print("-" * 50)
    
    # Create invalid Firebase config
    create_invalid_firebase_config()
    
    # Try to import and check Firebase config manager
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        
        # Force reload of configuration
        config_manager = get_firebase_config_manager()
        config_manager.load_configuration()
        
        if config_manager.is_configured():
            print("❌ FAIL: Config manager reports invalid config as valid")
            return False
        else:
            print("✅ PASS: Config manager correctly rejects invalid configuration")
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Error testing invalid config: {e}")
        return False

def test_firebase_integration_availability():
    """Test Firebase integration availability"""
    print("\n🧪 Test 3: Firebase Integration Availability")
    print("-" * 50)
    
    try:
        from modules import firebase_integration
        
        print(f"Pyrebase Available: {firebase_integration.PYREBASE_AVAILABLE}")
        print(f"Firebase Available: {firebase_integration.FIREBASE_AVAILABLE}")
        
        if firebase_integration.PYREBASE_AVAILABLE:
            print("✅ PASS: Pyrebase is available")
        else:
            print("❌ FAIL: Pyrebase is not available (required for online-only mode)")
            return False
        
        # Test initialization with invalid config
        if not firebase_integration.initialize_firebase():
            print("✅ PASS: Firebase initialization correctly fails with invalid config")
            return True
        else:
            print("❌ FAIL: Firebase initialization should fail with invalid config")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error testing Firebase integration: {e}")
        return False

def test_online_only_enforcement():
    """Test that offline support is properly disabled"""
    print("\n🧪 Test 4: Online-Only Mode Enforcement")
    print("-" * 50)
    
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        
        config_manager = get_firebase_config_manager()
        
        # Check that offline support is disabled
        if config_manager.features.get('offline_support', True) == False:
            print("✅ PASS: Offline support is properly disabled")
        else:
            print("❌ FAIL: Offline support should be disabled")
            return False
        
        # Check that authentication is required
        if config_manager.security_settings and config_manager.security_settings.require_authentication:
            print("✅ PASS: Authentication is properly required")
            return True
        else:
            print("❌ FAIL: Authentication should be required")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error testing online-only enforcement: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Kitchen Dashboard v1.0.6 - Online-Only Mode Enforcement Test")
    print("=" * 70)
    print("⚠️ This test verifies that the application properly enforces online-only mode")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('kitchen_app.py'):
        print("❌ Please run this script from the Kitchen Dashboard root directory")
        return 1
    
    # Backup current configuration
    backup_files = backup_firebase_config()
    
    try:
        # Run tests
        tests = [
            ("No Firebase Configuration", test_no_firebase_config),
            ("Invalid Firebase Configuration", test_invalid_firebase_config),
            ("Firebase Integration Availability", test_firebase_integration_availability),
            ("Online-Only Mode Enforcement", test_online_only_enforcement),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Online-Only Mode Enforcement Test Results:")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Online-only mode is properly enforced.")
            return_code = 0
        else:
            print("⚠️ Some tests failed. Online-only mode enforcement needs attention.")
            return_code = 1
    
    finally:
        # Restore configuration
        restore_firebase_config(backup_files)
        print("\n🔄 Configuration restored")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
