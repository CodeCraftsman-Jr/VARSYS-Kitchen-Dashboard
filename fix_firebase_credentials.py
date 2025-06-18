#!/usr/bin/env python3
"""
Firebase Credentials Fix Script
This script helps diagnose and fix Firebase credential issues
"""

import os
import json
import shutil
from datetime import datetime

def check_firebase_credentials():
    """Check Firebase credentials and provide recommendations"""
    print("=== Firebase Credentials Diagnostic ===")
    print(f"Diagnostic started at: {datetime.now()}")
    print()
    
    # Check credential files
    credential_files = [
        "firebase_credentials.json",
        "secure_credentials/firebase_credentials.json", 
        "firebase-admin-key.json",
        "firebase_admin_config.json"
    ]
    
    print("Checking credential files:")
    valid_creds = []
    invalid_creds = []
    
    for cred_file in credential_files:
        if os.path.exists(cred_file):
            print(f"✅ Found: {cred_file}")
            
            # Validate the credential file
            validation = validate_credential_file(cred_file)
            if validation['valid']:
                valid_creds.append(cred_file)
                print(f"   ✅ Valid credentials")
                print(f"   Project ID: {validation.get('project_id', 'Unknown')}")
                print(f"   Client Email: {validation.get('client_email', 'Unknown')}")
            else:
                invalid_creds.append(cred_file)
                print(f"   ❌ Invalid credentials")
                for error in validation.get('errors', []):
                    print(f"      • {error}")
        else:
            print(f"❌ Missing: {cred_file}")
    
    print()
    
    # Check web config files
    web_config_files = [
        "firebase_web_config.json",
        "secure_credentials/firebase_web_config.json",
        "firebase_config.json"
    ]
    
    print("Checking web config files:")
    valid_web_configs = []
    
    for config_file in web_config_files:
        if os.path.exists(config_file):
            print(f"✅ Found: {config_file}")
            
            # Validate web config
            validation = validate_web_config_file(config_file)
            if validation['valid']:
                valid_web_configs.append(config_file)
                print(f"   ✅ Valid web config")
                print(f"   Project ID: {validation.get('project_id', 'Unknown')}")
            else:
                print(f"   ❌ Invalid web config")
                for error in validation.get('errors', []):
                    print(f"      • {error}")
        else:
            print(f"❌ Missing: {config_file}")
    
    print()
    
    # Provide recommendations
    print("=== Recommendations ===")
    
    if not valid_creds:
        print("❌ No valid Firebase service account credentials found!")
        print()
        print("To fix this:")
        print("1. Go to Firebase Console (https://console.firebase.google.com)")
        print("2. Select your project: kitchen-dashboard-c663a")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Save the downloaded file as 'secure_credentials/firebase_credentials.json'")
        print()
        
        # Check if we can copy from existing location
        if os.path.exists("secure_credentials/firebase_credentials.json"):
            print("Note: Found credentials in secure_credentials/ but they appear invalid.")
            print("You may need to regenerate the service account key.")
    else:
        print("✅ Valid Firebase credentials found!")
        
        # Check if we need to copy to the expected location
        expected_location = "secure_credentials/firebase_credentials.json"
        if expected_location not in valid_creds:
            # Find the first valid credential file
            source_file = valid_creds[0]
            print(f"Recommendation: Copy {source_file} to {expected_location}")
            
            if input("Would you like to copy it now? (y/n): ").lower() == 'y':
                try:
                    os.makedirs("secure_credentials", exist_ok=True)
                    shutil.copy2(source_file, expected_location)
                    print(f"✅ Copied {source_file} to {expected_location}")
                except Exception as e:
                    print(f"❌ Error copying file: {e}")
    
    if not valid_web_configs:
        print("❌ No valid Firebase web config found!")
        print("You may need to set up the web configuration.")
    else:
        print("✅ Valid Firebase web config found!")
    
    return len(valid_creds) > 0 and len(valid_web_configs) > 0

def validate_credential_file(file_path):
    """Validate a Firebase credential file"""
    validation = {
        'valid': False,
        'errors': []
    }
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            validation['errors'].append(f"Missing fields: {', '.join(missing_fields)}")
        
        # Check if it's a service account
        if data.get('type') != 'service_account':
            validation['errors'].append(f"Expected service_account, got: {data.get('type')}")
        
        # Check private key format
        private_key = data.get('private_key', '')
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            validation['errors'].append("Invalid private key format")
        
        # Store useful info
        validation['project_id'] = data.get('project_id')
        validation['client_email'] = data.get('client_email')
        
        # If no errors, it's valid
        if not validation['errors']:
            validation['valid'] = True
            
    except json.JSONDecodeError as e:
        validation['errors'].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        validation['errors'].append(f"Error reading file: {str(e)}")
    
    return validation

def validate_web_config_file(file_path):
    """Validate a Firebase web config file"""
    validation = {
        'valid': False,
        'errors': []
    }
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle different config structures
        config = data
        if 'firebase' in data:
            config = data['firebase']
        
        # Check required fields
        required_fields = ['apiKey', 'authDomain', 'projectId']
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            validation['errors'].append(f"Missing fields: {', '.join(missing_fields)}")
        
        # Store useful info
        validation['project_id'] = config.get('projectId')
        
        # If no errors, it's valid
        if not validation['errors']:
            validation['valid'] = True
            
    except json.JSONDecodeError as e:
        validation['errors'].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        validation['errors'].append(f"Error reading file: {str(e)}")
    
    return validation

def main():
    """Main function"""
    print("Firebase Credentials Fix Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("kitchen_app.py"):
        print("❌ Error: Please run this script from the Kitchen Dashboard root directory")
        return False
    
    # Check Firebase credentials
    success = check_firebase_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Firebase credentials check completed successfully!")
        print("Your Firebase setup appears to be correct.")
    else:
        print("⚠️ Firebase credentials need attention!")
        print("Please follow the recommendations above to fix the issues.")
    
    return success

if __name__ == "__main__":
    main()
