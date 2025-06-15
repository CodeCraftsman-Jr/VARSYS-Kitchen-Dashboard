#!/usr/bin/env python3
"""
Update Firebase Configuration for Kitchen Dashboard v1.0.6
This script updates the main firebase_config.json with actual Firebase credentials
"""

import os
import json
import sys
from datetime import datetime

def load_json_file(file_path):
    """Load JSON file safely"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def save_json_file(file_path, data):
    """Save JSON file safely"""
    try:
        # Create backup
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"📋 Created backup: {backup_path}")
        
        # Save new configuration
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False

def update_main_config():
    """Update main firebase_config.json with actual credentials"""
    print("🔧 Updating main Firebase configuration...")
    
    # Load current main config
    main_config = load_json_file('firebase_config.json')
    if not main_config:
        return False
    
    # Try to load actual Firebase web config
    web_config_paths = [
        'firebase_web_config.json',
        'secure_credentials/firebase_web_config.json'
    ]
    
    web_config = None
    web_config_source = None
    
    for path in web_config_paths:
        if os.path.exists(path):
            web_config = load_json_file(path)
            if web_config:
                web_config_source = path
                break
    
    if not web_config:
        print("⚠️ No valid Firebase web config found")
        print("   Available paths checked:")
        for path in web_config_paths:
            status = "✅ Found" if os.path.exists(path) else "❌ Missing"
            print(f"   - {path}: {status}")
        return False
    
    print(f"✅ Using Firebase web config from: {web_config_source}")
    
    # Update main config with actual credentials
    main_config['firebase'] = {
        'apiKey': web_config.get('apiKey', ''),
        'authDomain': web_config.get('authDomain', ''),
        'databaseURL': web_config.get('databaseURL', ''),
        'projectId': web_config.get('projectId', ''),
        'storageBucket': web_config.get('storageBucket', ''),
        'messagingSenderId': web_config.get('messagingSenderId', ''),
        'appId': web_config.get('appId', ''),
        'measurementId': web_config.get('measurementId', '')
    }
    
    # Ensure online-only mode settings
    main_config['features']['offline_support'] = False
    main_config['security']['require_authentication'] = True
    
    # Save updated configuration
    if save_json_file('firebase_config.json', main_config):
        print("✅ Main Firebase configuration updated successfully")
        
        # Display configuration summary
        firebase_config = main_config['firebase']
        print("\n📋 Updated Configuration Summary:")
        print(f"   Project ID: {firebase_config.get('projectId', 'Not set')}")
        print(f"   Auth Domain: {firebase_config.get('authDomain', 'Not set')}")
        print(f"   Database URL: {firebase_config.get('databaseURL', 'Not set')}")
        print(f"   Storage Bucket: {firebase_config.get('storageBucket', 'Not set')}")
        print(f"   App ID: {firebase_config.get('appId', 'Not set')}")
        
        # Security settings
        print(f"\n🔒 Security Settings:")
        print(f"   Authentication Required: {main_config['security']['require_authentication']}")
        print(f"   Offline Support: {main_config['features']['offline_support']} (Online-Only Mode)")
        print(f"   Session Timeout: {main_config['security']['session_timeout_hours']} hours")
        print(f"   Auto Logout on Idle: {main_config['security']['auto_logout_on_idle']}")
        
        return True
    else:
        print("❌ Failed to save updated configuration")
        return False

def verify_service_account():
    """Verify Firebase service account credentials"""
    print("\n🔑 Checking Firebase service account credentials...")
    
    service_account_paths = [
        'secure_credentials/firebase_credentials.json'
    ]
    
    for path in service_account_paths:
        if os.path.exists(path):
            service_account = load_json_file(path)
            if service_account:
                print(f"✅ Service account found: {path}")
                print(f"   Project ID: {service_account.get('project_id', 'Not set')}")
                print(f"   Client Email: {service_account.get('client_email', 'Not set')}")
                print(f"   Type: {service_account.get('type', 'Not set')}")
                return True
    
    print("⚠️ No Firebase service account credentials found")
    print("   This is required for admin operations")
    return False

def check_firebase_project_consistency():
    """Check that all Firebase configs use the same project"""
    print("\n🔍 Checking Firebase project consistency...")
    
    configs = {}
    
    # Check main config
    main_config = load_json_file('firebase_config.json')
    if main_config and main_config.get('firebase'):
        configs['main'] = main_config['firebase'].get('projectId')
    
    # Check web config
    web_config = load_json_file('firebase_web_config.json')
    if web_config:
        configs['web'] = web_config.get('projectId')
    
    # Check secure web config
    secure_web_config = load_json_file('secure_credentials/firebase_web_config.json')
    if secure_web_config:
        configs['secure_web'] = secure_web_config.get('projectId')
    
    # Check service account
    service_account = load_json_file('secure_credentials/firebase_credentials.json')
    if service_account:
        configs['service_account'] = service_account.get('project_id')
    
    # Check consistency
    project_ids = list(set(configs.values()))
    project_ids = [pid for pid in project_ids if pid]  # Remove None values
    
    if len(project_ids) == 1:
        print(f"✅ All configurations use the same project: {project_ids[0]}")
        return True
    elif len(project_ids) > 1:
        print(f"⚠️ Multiple project IDs found: {project_ids}")
        print("   Configuration details:")
        for config_name, project_id in configs.items():
            print(f"   - {config_name}: {project_id}")
        return False
    else:
        print("❌ No valid project IDs found in any configuration")
        return False

def main():
    """Main function"""
    print("🚀 Kitchen Dashboard v1.0.6 - Firebase Configuration Update")
    print("=" * 65)
    print("⚠️ This will update firebase_config.json with actual credentials")
    print("=" * 65)
    
    # Check current directory
    if not os.path.exists('kitchen_app.py'):
        print("❌ Please run this script from the Kitchen Dashboard root directory")
        return 1
    
    success = True
    
    # Update main configuration
    if not update_main_config():
        success = False
    
    # Verify service account
    if not verify_service_account():
        success = False
    
    # Check project consistency
    if not check_firebase_project_consistency():
        success = False
    
    print("\n" + "=" * 65)
    
    if success:
        print("🎉 Firebase configuration update completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Run: python test_firebase_integration.py")
        print("2. Test authentication: python kitchen_app.py")
        print("3. Verify cloud sync functionality")
        print("\n⚠️ Remember: This application requires online authentication")
        return 0
    else:
        print("⚠️ Firebase configuration update completed with warnings")
        print("\n📋 Please review the issues above and:")
        print("1. Ensure all Firebase configuration files are present")
        print("2. Verify Firebase project settings")
        print("3. Check that all configs use the same project ID")
        return 1

if __name__ == "__main__":
    sys.exit(main())
