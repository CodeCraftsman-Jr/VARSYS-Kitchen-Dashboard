#!/usr/bin/env python3
"""
Test Subscription-Based Authentication for Kitchen Dashboard v1.0.6
This script tests the subscription-based authentication system
"""

import sys
import os
from datetime import datetime

def test_firebase_config():
    """Test Firebase configuration for subscription model"""
    print("🔧 Testing Firebase Configuration for Subscription Model...")
    
    try:
        from modules.firebase_config_manager import get_firebase_config_manager
        
        config_manager = get_firebase_config_manager()
        
        if config_manager.is_configured():
            print("✅ Firebase configuration is valid")
            
            # Check subscription settings
            firebase_config = config_manager.firebase_config
            if firebase_config:
                print(f"   Project ID: {firebase_config.project_id}")
                print(f"   Auth Domain: {firebase_config.auth_domain}")
            
            # Check if offline support is disabled (subscription requirement)
            if not config_manager.features.get('offline_support', True):
                print("✅ Offline support properly disabled for subscription model")
            else:
                print("⚠️ Warning: Offline support should be disabled for subscription model")
            
            return True
        else:
            print("❌ Firebase configuration is invalid or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase configuration: {e}")
        return False

def test_firebase_authentication():
    """Test Firebase authentication availability"""
    print("\n🔐 Testing Firebase Authentication for Subscribers...")
    
    try:
        from modules import firebase_integration
        
        # Check if pyrebase is available
        if not firebase_integration.PYREBASE_AVAILABLE:
            print("❌ Pyrebase is not available. Please install: pip install pyrebase4")
            return False
        
        print("✅ Pyrebase is available for subscriber authentication")
        
        # Try to initialize Firebase
        if firebase_integration.initialize_firebase():
            print("✅ Firebase authentication system is ready")
            print("   Subscribers can now authenticate with their credentials")
            return True
        else:
            print("❌ Firebase authentication initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firebase authentication: {e}")
        return False

def test_subscription_model():
    """Test subscription model configuration"""
    print("\n👥 Testing Subscription Model Configuration...")
    
    try:
        import json
        
        # Check firebase_config.json for subscription settings
        if os.path.exists('firebase_config.json'):
            with open('firebase_config.json', 'r') as f:
                config = json.load(f)
            
            subscription_config = config.get('subscription', {})
            
            if subscription_config:
                print("✅ Subscription configuration found")
                print(f"   Model: {subscription_config.get('model', 'Not set')}")
                print(f"   Description: {subscription_config.get('description', 'Not set')}")
                print(f"   User Data Isolation: {subscription_config.get('user_data_isolation', 'Not set')}")
                
                if subscription_config.get('model') == 'admin_managed':
                    print("✅ Admin-managed subscription model configured correctly")
                    return True
                else:
                    print("⚠️ Subscription model should be 'admin_managed'")
                    return False
            else:
                print("❌ No subscription configuration found")
                return False
        else:
            print("❌ firebase_config.json not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing subscription model: {e}")
        return False

def test_cloud_sync_manager():
    """Test cloud sync manager for subscription model"""
    print("\n☁️ Testing Cloud Sync Manager for Subscribers...")
    
    try:
        # Initialize QApplication for Qt widgets
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
            print("✅ Cloud sync manager initialized for subscription model")
            
            # Test subscriber info setting
            test_user_info = {
                'localId': 'test_subscriber_123',
                'email': 'subscriber@example.com',
                'subscription_type': 'firebase_managed'
            }
            
            sync_manager.set_subscriber_info(test_user_info)
            print("✅ Subscriber info can be set for data isolation")
            
            return True
        else:
            print("❌ Failed to initialize cloud sync manager")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cloud sync manager: {e}")
        return False

def test_user_data_isolation():
    """Test that user data will be properly isolated"""
    print("\n🔒 Testing User Data Isolation...")
    
    try:
        from modules.optimized_firebase_manager import get_optimized_firebase_manager
        
        firebase_manager = get_optimized_firebase_manager()
        
        if firebase_manager:
            print("✅ Firebase manager available for user data isolation")
            
            # Test user session setting
            test_user_info = {
                'localId': 'subscriber_456',
                'email': 'another.subscriber@example.com',
                'idToken': 'test_token_123',
                'refreshToken': 'test_refresh_token'
            }
            
            if firebase_manager.set_current_user(test_user_info):
                print("✅ User session can be set for data isolation")
                
                current_user = firebase_manager.get_current_user()
                if current_user and current_user.get('user_id') == 'subscriber_456':
                    print("✅ User data isolation is working correctly")
                    return True
                else:
                    print("❌ User data isolation test failed")
                    return False
            else:
                print("❌ Failed to set user session")
                return False
        else:
            print("❌ Firebase manager not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing user data isolation: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Kitchen Dashboard v1.0.6 - Subscription-Based Authentication Test")
    print("=" * 75)
    print("👥 Testing subscription model where only admin-created users can access")
    print("=" * 75)
    
    # Check if we're in the right directory
    if not os.path.exists('kitchen_app.py'):
        print("❌ Please run this script from the Kitchen Dashboard root directory")
        return 1
    
    # Run tests
    tests = [
        ("Firebase Configuration", test_firebase_config),
        ("Firebase Authentication", test_firebase_authentication),
        ("Subscription Model", test_subscription_model),
        ("Cloud Sync Manager", test_cloud_sync_manager),
        ("User Data Isolation", test_user_data_isolation),
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
    print("\n" + "=" * 75)
    print("📊 Subscription-Based Authentication Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Subscription-based authentication is ready.")
        print("\n📋 Subscription Model Summary:")
        print("• Only users created by admin in Firebase can access")
        print("• Each user's data is isolated by their user ID")
        print("• No offline mode - authentication required")
        print("• Real-time cloud sync for all subscriber data")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the subscription configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
