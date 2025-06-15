#!/usr/bin/env python3
"""
Reset Password for Firebase Authentication
For Kitchen Dashboard Subscription Model
"""

import json
import pyrebase

def load_firebase_config():
    """Load Firebase configuration from file"""
    try:
        with open('firebase_config.json', 'r') as f:
            config = json.load(f)
        return config['firebase']
    except Exception as e:
        print(f"❌ Error loading Firebase config: {e}")
        return None

def reset_password():
    """Send password reset email"""
    print("🔧 Kitchen Dashboard - Password Reset")
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
        
        # Get email
        email = input("📧 Enter email address: ").strip()
        if not email:
            print("❌ Email is required")
            return False
        
        # Send password reset email
        print(f"\n🔄 Sending password reset email to: {email}")
        auth.send_password_reset_email(email)
        
        print(f"✅ Password reset email sent successfully!")
        print(f"📧 Check your email: {email}")
        print("📨 Follow the link in the email to reset your password")
        
        return True
            
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_NOT_FOUND" in error_msg:
            print(f"❌ No user found with email: {email}")
            print("💡 Make sure the email is correct or create a new account")
        elif "INVALID_EMAIL" in error_msg:
            print("❌ Invalid email format")
        else:
            print(f"❌ Error sending password reset: {e}")
        return False

def test_login():
    """Test login with credentials"""
    print("\n🔧 Test Login")
    print("=" * 30)
    
    # Load Firebase config
    firebase_config = load_firebase_config()
    if not firebase_config:
        return False
    
    try:
        # Initialize Firebase
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        
        # Get credentials
        email = input("📧 Enter email: ").strip()
        password = input("🔒 Enter password: ").strip()
        
        print(f"\n🔄 Testing login for: {email}")
        user = auth.sign_in_with_email_and_password(email, password)
        
        if user:
            print("✅ Login successful!")
            print(f"🆔 User ID: {user['localId']}")
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_msg:
            print("❌ Invalid email or password")
        elif "EMAIL_NOT_FOUND" in error_msg:
            print("❌ No user found with this email")
        elif "INVALID_PASSWORD" in error_msg:
            print("❌ Incorrect password")
        else:
            print(f"❌ Login error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Kitchen Dashboard Authentication Helper")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Send password reset email")
        print("2. Test login")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            reset_password()
        elif choice == "2":
            test_login()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
