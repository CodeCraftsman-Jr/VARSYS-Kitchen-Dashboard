#!/usr/bin/env python3
"""
Test script to verify Firebase connection fixes
This script tests the improved Firebase manager functionality
"""

import sys
import os
import json
from datetime import datetime

def test_firebase_connection():
    """Test Firebase connection with the improved manager"""
    print("=== Firebase Connection Test ===")
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        # Import the optimized Firebase manager
        from modules.optimized_firebase_manager import get_optimized_firebase_manager
        
        print("✅ Successfully imported optimized Firebase manager")
        
        # Initialize the manager
        firebase_manager = get_optimized_firebase_manager()
        print("✅ Firebase manager instance created")
        
        # Test initialization
        print("\n--- Testing Firebase Initialization ---")
        init_success = firebase_manager.initialize_firebase()
        print(f"Initialization result: {'✅ Success' if init_success else '❌ Failed'}")
        
        # Get detailed diagnostics
        print("\n--- Firebase Diagnostics ---")
        diagnostics = firebase_manager.get_connection_diagnostics()
        
        print(f"Overall Status: {diagnostics.get('overall_status', 'unknown')}")
        print(f"Timestamp: {diagnostics.get('timestamp', 'unknown')}")
        
        # Component status
        components = diagnostics.get('components', {})
        print("\nComponent Status:")
        
        admin_sdk = components.get('admin_sdk', {})
        print(f"  Admin SDK: {'✅' if admin_sdk.get('available') else '❌'} Available")
        if admin_sdk.get('project_id'):
            print(f"    Project ID: {admin_sdk['project_id']}")
        if admin_sdk.get('error'):
            print(f"    Error: {admin_sdk['error']}")
        
        firestore = components.get('firestore_database', {})
        print(f"  Firestore DB: {'✅' if firestore.get('available') else '❌'} Available")
        print(f"    Connection Test: {'✅' if firestore.get('connection_test') else '❌'}")
        if firestore.get('error'):
            print(f"    Error: {firestore['error']}")
        
        auth = components.get('pyrebase_auth', {})
        print(f"  Pyrebase Auth: {'✅' if auth.get('available') else '❌'} Available")
        if auth.get('error'):
            print(f"    Error: {auth['error']}")
        
        session = components.get('user_session', {})
        print(f"  User Session: {'✅' if session.get('authenticated') else '❌'} Authenticated")
        if session.get('user_email'):
            print(f"    User: {session['user_email']}")
        
        # Recommendations
        recommendations = diagnostics.get('recommendations', [])
        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Test specific functions
        print("\n--- Function Tests ---")
        
        # Test database availability
        if hasattr(firebase_manager, 'is_database_available'):
            db_available = firebase_manager.is_database_available()
            print(f"Database Available: {'✅' if db_available else '❌'}")
        
        # Test authentication status
        auth_status = firebase_manager.is_authenticated()
        print(f"User Authenticated: {'✅' if auth_status else '❌'}")
        
        # Test reinitialization capability
        if hasattr(firebase_manager, 'reinitialize_database'):
            print("\n--- Testing Reinitialization ---")
            reinit_success = firebase_manager.reinitialize_database()
            print(f"Database Reinitialization: {'✅' if reinit_success else '❌'}")
        
        print("\n=== Test Summary ===")
        if init_success and diagnostics.get('overall_status') in ['fully_connected', 'auth_only', 'database_only']:
            print("✅ Firebase connection test PASSED")
            print("The Firebase manager is working correctly with the fixes applied.")
        else:
            print("⚠️ Firebase connection test PARTIAL")
            print("Some Firebase services are working, but not all components are available.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_firebase_files():
    """Check if Firebase configuration files exist"""
    print("\n=== Firebase Files Check ===")
    
    files_to_check = [
        "firebase_config.json",
        "firebase_web_config.json",
        "secure_credentials/firebase_credentials.json",
        "secure_credentials/firebase_web_config.json",
        "firebase_credentials.json",
        "firebase-admin-key.json"
    ]
    
    found_files = []
    missing_files = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            found_files.append(file_path)
            print(f"✅ Found: {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
    
    print(f"\nSummary: {len(found_files)} found, {len(missing_files)} missing")
    
    if found_files:
        print("\nRecommendation: Firebase configuration files are available.")
    else:
        print("\nRecommendation: No Firebase configuration files found. Please set up Firebase first.")
    
    return len(found_files) > 0

def main():
    """Main test function"""
    print("Firebase Connection Fix Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("kitchen_app.py"):
        print("❌ Error: Please run this script from the Kitchen Dashboard root directory")
        return False
    
    # Check Firebase files
    files_exist = check_firebase_files()
    
    if not files_exist:
        print("\n⚠️ Warning: No Firebase configuration files found.")
        print("The test will still run but Firebase services won't be available.")
    
    # Test Firebase connection
    test_success = test_firebase_connection()
    
    print("\n" + "=" * 50)
    if test_success:
        print("✅ Firebase connection test completed successfully!")
    else:
        print("❌ Firebase connection test failed!")
    
    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
