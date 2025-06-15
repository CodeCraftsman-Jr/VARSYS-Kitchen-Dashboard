#!/usr/bin/env python3
"""
Create User Account in Firebase Authentication
For Kitchen Dashboard Subscription Model
"""

import json
import pyrebase
from getpass import getpass

def load_firebase_config():
    """Load Firebase configuration from file"""
    try:
        with open('firebase_config.json', 'r') as f:
            config = json.load(f)
        return config['firebase']
    except Exception as e:
        print(f"❌ Error loading Firebase config: {e}")
        return None

def create_user_account():
    """Create a new user account in Firebase Authentication"""
    print("🔧 Kitchen Dashboard - Create User Account")
    print("=" * 50)
    
    # Load Firebase config
    firebase_config = load_firebase_config()
    if not firebase_config:
        return False
    
    try:
        # Initialize Firebase
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        
        print("✅ Firebase initialized successfully")
        
        # Get user details
        email = input("📧 Enter email address: ").strip()
        if not email:
            print("❌ Email is required")
            return False
        
        password = getpass("🔒 Enter password: ").strip()
        if not password:
            print("❌ Password is required")
            return False
        
        confirm_password = getpass("🔒 Confirm password: ").strip()
        if password != confirm_password:
            print("❌ Passwords don't match")
            return False
        
        # Create user account
        print(f"\n🔄 Creating user account for: {email}")
        user = auth.create_user_with_email_and_password(email, password)
        
        if user:
            print(f"✅ User account created successfully!")
            print(f"📧 Email: {email}")
            print(f"🆔 User ID: {user['localId']}")
            print(f"🔑 ID Token: {user['idToken'][:20]}...")
            
            # Send email verification (optional)
            try:
                auth.send_email_verification(user['idToken'])
                print("📨 Email verification sent")
            except Exception as e:
                print(f"⚠️ Could not send email verification: {e}")
            
            return True
        else:
            print("❌ Failed to create user account")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            print(f"⚠️ User account already exists for: {email}")
            print("💡 Try logging in with existing credentials")
        elif "WEAK_PASSWORD" in error_msg:
            print("❌ Password is too weak. Use at least 6 characters")
        elif "INVALID_EMAIL" in error_msg:
            print("❌ Invalid email format")
        else:
            print(f"❌ Error creating user: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Kitchen Dashboard User Creation Tool")
    print("=" * 50)
    
    success = create_user_account()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("You can now login to Kitchen Dashboard with your credentials")
    else:
        print("\n❌ FAILED!")
        print("Please try again or create user via Firebase Console")
    
    print("\n📋 Alternative: Create user via Firebase Console:")
    print("1. Go to: https://console.firebase.google.com/project/kitchen-dashboard-c663a/authentication/users")
    print("2. Click 'Add User'")
    print("3. Enter email and password")
    print("4. Click 'Add User'")

if __name__ == "__main__":
    main()
