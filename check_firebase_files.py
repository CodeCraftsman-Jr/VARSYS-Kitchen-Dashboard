#!/usr/bin/env python3
"""
Check Firebase Configuration Files for Kitchen Dashboard v1.0.6 (Online-Only Mode)
This script verifies that all required Firebase configuration files are present and valid.
"""

import os
import json
import sys

def check_firebase_config_json():
    """Check if firebase_config.json exists and is valid"""
    print("🔧 Checking firebase_config.json...")
    
    config_file = "firebase_config.json"
    
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check required Firebase fields
        firebase_config = config.get('firebase', {})
        required_fields = ['apiKey', 'authDomain', 'projectId']
        
        missing_fields = []
        for field in required_fields:
            if not firebase_config.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields in firebase_config.json: {', '.join(missing_fields)}")
            return False
        
        # Check that offline support is disabled
        features = config.get('features', {})
        if features.get('offline_support', True):
            print("⚠️ Warning: offline_support should be false for online-only mode")
        
        print("✅ firebase_config.json is valid")
        print(f"   Project ID: {firebase_config.get('projectId', 'Not set')}")
        print(f"   Auth Domain: {firebase_config.get('authDomain', 'Not set')}")
        print(f"   Offline Support: {features.get('offline_support', 'Not set')} (should be false)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_file}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {config_file}: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    print("\n🌍 Checking .env file...")
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file found")
        
        # Check for Firebase environment variables
        firebase_vars = []
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('FIREBASE_'):
                        firebase_vars.append(line.strip().split('=')[0])
            
            if firebase_vars:
                print(f"   Found Firebase variables: {', '.join(firebase_vars)}")
            else:
                print("   No Firebase environment variables found")
                
        except Exception as e:
            print(f"⚠️ Error reading .env file: {e}")
        
        return True
    else:
        print("ℹ️ .env file not found (optional)")
        return True

def check_env_template():
    """Check if .env.template exists"""
    print("\n📋 Checking .env.template...")
    
    template_file = ".env.template"
    
    if os.path.exists(template_file):
        print("✅ .env.template found")
        return True
    else:
        print("❌ .env.template not found")
        return False

def check_firebase_setup_docs():
    """Check if Firebase setup documentation exists"""
    print("\n📚 Checking Firebase setup documentation...")
    
    setup_file = "FIREBASE_SETUP.md"
    
    if os.path.exists(setup_file):
        print("✅ FIREBASE_SETUP.md found")
        return True
    else:
        print("❌ FIREBASE_SETUP.md not found")
        return False

def check_firebase_modules():
    """Check if Firebase modules exist"""
    print("\n🐍 Checking Firebase modules...")
    
    modules_to_check = [
        "modules/firebase_config_manager.py",
        "modules/firebase_config_widget.py",
        "modules/firebase_integration.py",
        "modules/optimized_firebase_manager.py",
        "modules/cloud_sync_manager.py",
        "modules/enhanced_auth_widget.py"
    ]
    
    all_present = True
    
    for module in modules_to_check:
        if os.path.exists(module):
            print(f"✅ {module}")
        else:
            print(f"❌ {module} not found")
            all_present = False
    
    return all_present

def main():
    """Main function to check all Firebase files"""
    print("🔍 Kitchen Dashboard v1.0.6 - Firebase Files Check (Online-Only Mode)")
    print("=" * 70)
    print("⚠️ This application requires all Firebase files for online authentication")
    print("=" * 70)
    
    checks = [
        ("Firebase Configuration JSON", check_firebase_config_json),
        ("Environment File", check_env_file),
        ("Environment Template", check_env_template),
        ("Firebase Setup Documentation", check_firebase_setup_docs),
        ("Firebase Python Modules", check_firebase_modules),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 File Check Results:")
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {check_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All Firebase files are present and configured!")
        print("\n📋 Next Steps:")
        print("1. Configure your Firebase project settings in firebase_config.json")
        print("2. Run: python test_firebase_integration.py")
        print("3. Run: python kitchen_app.py")
        return True
    else:
        print("⚠️ Some Firebase files are missing or misconfigured.")
        print("\n📋 Required Actions:")
        print("1. Ensure all Firebase modules are present")
        print("2. Configure firebase_config.json with your Firebase project settings")
        print("3. See FIREBASE_SETUP.md for detailed instructions")
        print("4. Remember: This application requires online authentication")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
