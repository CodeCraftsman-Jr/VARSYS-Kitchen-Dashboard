#!/usr/bin/env python3
"""
Test Firebase Integration for Kitchen Dashboard v1.0.6 (Online-Only Mode)
This script tests the Firebase authentication and cloud sync functionality.
⚠️ IMPORTANT: This application requires online authentication and does not support offline mode.
"""

import sys
import os
import json
from datetime import datetime

def test_firebase_config():
    """Test Firebase configuration"""
    print("🔧 Testing Firebase Configuration...")
    
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        
        config_manager = get_firebase_config_manager()
        
        if config_manager.is_configured():
            print("✅ Firebase configuration is valid")
            
            # Print configuration summary (without sensitive data)
            firebase_config = config_manager.firebase_config
            if firebase_config:
                print(f"   Project ID: {firebase_config.project_id}")
                print(f"   Auth Domain: {firebase_config.auth_domain}")
                print(f"   API Key: {'*' * (len(firebase_config.api_key) - 4) + firebase_config.api_key[-4:] if firebase_config.api_key else 'Not set'}")
            
            return True
        else:
            print("❌ Firebase configuration is invalid or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase configuration: {e}")
        return False

def test_firebase_connection():
    """Test Firebase connection"""
    print("\n🔗 Testing Firebase Connection...")
    
    try:
        from modules import firebase_integration
        
        # Check if pyrebase is available
        if not firebase_integration.PYREBASE_AVAILABLE:
            print("❌ Pyrebase is not available. Please install: pip install pyrebase4")
            return False
        
        # Try to initialize Firebase
        if firebase_integration.initialize_firebase():
            print("✅ Firebase connection successful")
            return True
        else:
            print("❌ Firebase connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase connection: {e}")
        return False

def test_optimized_firebase_manager():
    """Test optimized Firebase manager"""
    print("\n⚡ Testing Optimized Firebase Manager...")
    
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        from modules.optimized_firebase_manager import get_optimized_firebase_manager
        
        config_manager = get_firebase_config_manager()
        firebase_manager = get_optimized_firebase_manager(config_manager)
        
        if firebase_manager:
            print("✅ Optimized Firebase manager initialized")
            
            # Test usage statistics
            stats = firebase_manager.get_usage_statistics()
            print(f"   Daily reads: {stats['daily_reads']}/{stats['max_reads']}")
            print(f"   Daily writes: {stats['daily_writes']}/{stats['max_writes']}")
            
            return True
        else:
            print("❌ Failed to initialize optimized Firebase manager")
            return False
            
    except Exception as e:
        print(f"❌ Error testing optimized Firebase manager: {e}")
        return False

def test_cloud_sync_manager():
    """Test cloud sync manager"""
    print("\n☁️ Testing Cloud Sync Manager...")

    try:
        # Initialize QApplication first for Qt widgets
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication(sys.argv)

        from modules.cloud_sync_manager import CloudSyncManager
        import pandas as pd

        # Create sample data
        sample_data = {
            'test_table': pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Test Item 1', 'Test Item 2', 'Test Item 3'],
                'timestamp': [datetime.now().isoformat()] * 3
            })
        }

        sync_manager = CloudSyncManager(sample_data)

        if sync_manager:
            print("✅ Cloud sync manager initialized")
            return True
        else:
            print("❌ Failed to initialize cloud sync manager")
            return False

    except Exception as e:
        print(f"❌ Error testing cloud sync manager: {e}")
        return False

def test_authentication_widget():
    """Test authentication widget"""
    print("\n🔐 Testing Authentication Widget...")

    try:
        # Initialize QApplication first for Qt widgets
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication(sys.argv)

        from modules.enhanced_auth_widget import EnhancedAuthWidget

        auth_widget = EnhancedAuthWidget()

        if auth_widget:
            print("✅ Authentication widget initialized")
            return True
        else:
            print("❌ Failed to initialize authentication widget")
            return False

    except Exception as e:
        print(f"❌ Error testing authentication widget: {e}")
        return False

def test_online_only_mode():
    """Test that online-only mode is enforced"""
    print("\n🌐 Testing Online-Only Mode Enforcement...")

    try:
        from modules.firebase_config_manager import get_firebase_config_manager

        config_manager = get_firebase_config_manager()

        # Check that offline support is disabled
        if config_manager.features.get('offline_support', True) == False:
            print("✅ Offline support is properly disabled")
            return True
        else:
            print("❌ Offline support should be disabled for online-only mode")
            return False

    except Exception as e:
        print(f"❌ Error testing online-only mode: {e}")
        return False

def run_all_tests():
    """Run all Firebase integration tests"""
    print("🚀 Kitchen Dashboard v1.0.6 - Firebase Integration Test (Online-Only Mode)")
    print("=" * 70)
    print("⚠️  This application requires online authentication - no offline mode available")
    print("=" * 70)

    tests = [
        ("Firebase Configuration", test_firebase_config),
        ("Firebase Connection", test_firebase_connection),
        ("Optimized Firebase Manager", test_optimized_firebase_manager),
        ("Cloud Sync Manager", test_cloud_sync_manager),
        ("Authentication Widget", test_authentication_widget),
        ("Online-Only Mode Enforcement", test_online_only_mode),
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
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Firebase integration is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration and dependencies.")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        
        if not success:
            print("\n📋 Troubleshooting Tips (Online-Only Mode):")
            print("1. Ensure firebase_config.json is properly configured")
            print("2. Install required packages: pip install pyrebase4 firebase-admin")
            print("3. Check Firebase project settings and authentication")
            print("4. ⚠️ CRITICAL: Verify stable internet connection (required at all times)")
            print("5. Ensure Firebase Authentication is enabled in your project")
            print("6. Check that Email/Password authentication is enabled")
            print("7. See FIREBASE_SETUP.md for detailed setup instructions")
            print("8. ⚠️ Remember: This application does not support offline mode")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
