#!/usr/bin/env python3
"""
Simple Firebase test without hanging
"""

import os
import json
from datetime import datetime

def test_firebase_simple():
    """Simple Firebase test"""
    print("=== Simple Firebase Test ===")
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        # Test Firebase Admin SDK import
        print("Testing Firebase imports...")
        import firebase_admin
        from firebase_admin import credentials, firestore
        print("✅ Firebase Admin SDK imported successfully")
        
        # Test Pyrebase import
        import pyrebase
        print("✅ Pyrebase imported successfully")
        
        # Test credential file loading
        cred_path = "secure_credentials/firebase_credentials.json"
        if os.path.exists(cred_path):
            print(f"✅ Found credentials file: {cred_path}")
            
            # Try to load credentials
            try:
                cred = credentials.Certificate(cred_path)
                print("✅ Credentials loaded successfully")
                
                # Try to initialize Firebase (without connecting)
                if not firebase_admin._apps:
                    app = firebase_admin.initialize_app(cred)
                    print("✅ Firebase Admin app initialized")
                    
                    # Get project ID
                    project_id = app.project_id
                    print(f"✅ Project ID: {project_id}")
                    
                    # Try to create Firestore client (this might fail with JWT error)
                    print("Testing Firestore client creation...")
                    try:
                        db = firestore.client()
                        print("✅ Firestore client created successfully")
                        
                        # Don't test actual connection to avoid hanging
                        print("⚠️ Skipping connection test to avoid hanging")
                        
                    except Exception as firestore_error:
                        error_str = str(firestore_error)
                        print(f"❌ Firestore client creation failed: {error_str}")
                        
                        if "invalid_grant" in error_str.lower():
                            print("❌ JWT Signature Error - Credentials are invalid or expired")
                            print("   Solution: Regenerate the service account key in Firebase Console")
                        elif "permission" in error_str.lower():
                            print("❌ Permission Error - Service account lacks required permissions")
                        else:
                            print(f"❌ Unknown Firestore error: {error_str}")
                        
                        return False
                        
                else:
                    print("✅ Using existing Firebase Admin app")
                    
            except Exception as cred_error:
                print(f"❌ Credential loading failed: {cred_error}")
                return False
                
        else:
            print(f"❌ Credentials file not found: {cred_path}")
            return False
        
        # Test web config
        web_config_path = "firebase_web_config.json"
        if os.path.exists(web_config_path):
            print(f"✅ Found web config: {web_config_path}")
            
            try:
                with open(web_config_path, 'r') as f:
                    config = json.load(f)
                
                # Initialize Pyrebase
                pyrebase_app = pyrebase.initialize_app(config)
                auth = pyrebase_app.auth()
                print("✅ Pyrebase authentication initialized")
                
            except Exception as pyrebase_error:
                print(f"❌ Pyrebase initialization failed: {pyrebase_error}")
                return False
        else:
            print(f"❌ Web config file not found: {web_config_path}")
            return False
        
        print("\n✅ All Firebase components initialized successfully!")
        print("Note: Actual database connection was not tested to avoid hanging.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure Firebase libraries are installed: pip install firebase-admin pyrebase4")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_system_time():
    """Check if system time is correct (important for JWT)"""
    print("\n=== System Time Check ===")
    
    import time
    from datetime import timezone
    
    # Get current time
    local_time = datetime.now()
    utc_time = datetime.now(timezone.utc)
    
    print(f"Local time: {local_time}")
    print(f"UTC time: {utc_time}")
    
    # Check if time seems reasonable (not too far off)
    expected_year = 2025
    if local_time.year != expected_year:
        print(f"⚠️ Warning: System time year is {local_time.year}, expected {expected_year}")
        print("   Incorrect system time can cause JWT signature errors")
        return False
    
    print("✅ System time appears correct")
    return True

def suggest_solutions():
    """Suggest solutions for common Firebase issues"""
    print("\n=== Common Solutions ===")
    print()
    print("If you're getting 'Invalid JWT Signature' errors:")
    print("1. Regenerate Firebase service account key:")
    print("   - Go to Firebase Console > Project Settings > Service Accounts")
    print("   - Click 'Generate new private key'")
    print("   - Replace secure_credentials/firebase_credentials.json")
    print()
    print("2. Check system time:")
    print("   - Ensure your computer's date/time is correct")
    print("   - JWT tokens are time-sensitive")
    print()
    print("3. Verify project permissions:")
    print("   - Ensure the service account has Firestore permissions")
    print("   - Check Firebase project is active and billing is set up")
    print()
    print("4. Network issues:")
    print("   - Check internet connection")
    print("   - Verify firewall/proxy settings")

def main():
    """Main function"""
    print("Simple Firebase Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("kitchen_app.py"):
        print("❌ Error: Please run this script from the Kitchen Dashboard root directory")
        return False
    
    # Check system time
    time_ok = check_system_time()
    
    # Test Firebase
    firebase_ok = test_firebase_simple()
    
    # Provide suggestions
    suggest_solutions()
    
    print("\n" + "=" * 50)
    if firebase_ok and time_ok:
        print("✅ Firebase test completed successfully!")
    else:
        print("⚠️ Firebase test found issues - see recommendations above")
    
    return firebase_ok

if __name__ == "__main__":
    main()
