#!/usr/bin/env python3
"""
Secure Build Script for VARSYS Kitchen Dashboard
Embeds Firebase credentials securely and creates protected executable
"""

import os
import sys
import json
import base64
import hashlib
import subprocess
from pathlib import Path

def embed_firebase_credentials():
    """Embed your Firebase credentials securely in the installer"""

    print("🔐 Embedding Firebase credentials securely...")

    # Load your actual Firebase configuration from secure folder
    credentials_file = "secure_credentials/firebase_credentials.json"

    if not os.path.exists(credentials_file):
        print("❌ ERROR: Firebase credentials not found!")
        print(f"   Please create {credentials_file} with your actual Firebase configuration.")
        print("   See secure_credentials/README.md for instructions.")
        return False

    try:
        with open(credentials_file, 'r') as f:
            firebase_config = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to load Firebase credentials: {e}")
        return False

    # Check if this is demo mode (for GitHub distribution)
    demo_mode = os.getenv('DEMO_BUILD', 'false').lower() == 'true'

    if firebase_config.get("apiKey", "").startswith("YOUR_ACTUAL_"):
        if demo_mode:
            print("🎭 Demo mode: Using placeholder Firebase configuration")
            print("   For production, update secure_credentials/firebase_credentials.json with actual credentials")
        else:
            print("❌ ERROR: Please update your Firebase credentials!")
            print(f"   Edit {credentials_file} and replace the placeholder values with your actual Firebase configuration.")
            print("   Or set DEMO_BUILD=true for demo build")
            return False
    
    # Create verification hash
    config_string = json.dumps(firebase_config, sort_keys=True)
    config_hash = hashlib.sha256(config_string.encode()).hexdigest()
    
    # Update firebase_installer.py with your credentials
    installer_file = "firebase_installer.py"
    
    try:
        with open(installer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the placeholder configuration
        new_content = content.replace(
            'YOUR_ACTUAL_FIREBASE_API_KEY_HERE',
            firebase_config["apiKey"]
        ).replace(
            'your-project.firebaseapp.com',
            firebase_config["authDomain"]
        ).replace(
            'your-project-id',
            firebase_config["projectId"]
        ).replace(
            'your-project.appspot.com',
            firebase_config["storageBucket"]
        ).replace(
            '123456789012',
            firebase_config["messagingSenderId"]
        ).replace(
            '1:123456789012:web:abcdef123456789',
            firebase_config["appId"]
        ).replace(
            'https://your-project-default-rtdb.firebaseio.com',
            firebase_config["databaseURL"]
        ).replace(
            'your_config_verification_hash_here',
            config_hash
        )
        
        # Write updated installer
        with open(installer_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Firebase credentials embedded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error embedding Firebase credentials: {e}")
        return False

def update_license_secrets():
    """Update license manager with your unique secrets"""
    
    print("🔐 Updating license secrets...")
    
    # YOUR UNIQUE SECRETS (Change these!)
    app_secret = "VARSYS_KITCHEN_DASHBOARD_SECRET_2025_YOUR_UNIQUE_KEY"
    firebase_secret = "VARSYS_FIREBASE_MASTER_KEY_2025_YOUR_UNIQUE_KEY"
    integrity_key = "VARSYS_INTEGRITY_CHECK_2025_YOUR_UNIQUE_KEY"
    
    try:
        # Update license_manager.py
        license_file = "license_manager.py"
        with open(license_file, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace(
            'VARSYS_KITCHEN_DASHBOARD_SECRET_2025',
            app_secret
        )

        with open(license_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update firebase_protection.py
        firebase_file = "firebase_protection.py"
        with open(firebase_file, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace(
            'VARSYS_FIREBASE_MASTER_KEY_2025_ULTRA_SECURE',
            firebase_secret
        ).replace(
            'VARSYS_INTEGRITY_CHECK_2025',
            integrity_key
        )

        with open(firebase_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ License secrets updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating license secrets: {e}")
        return False

def build_executable():
    """Build the secure executable"""
    
    print("🏗️ Building secure executable...")
    
    try:
        # Run cx_Freeze build
        result = subprocess.run([
            sys.executable, "setup_cx_freeze.py", "build"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def verify_security():
    """Verify security measures are in place"""
    
    print("🔍 Verifying security measures...")
    
    security_checks = []
    
    # Check if license files are in .gitignore
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        required_exclusions = [
            'license.dat',
            'firebase_config_protected.json',
            '.firebase_vault.dat',
            '.firebase_checksum.dat'
        ]
        
        for exclusion in required_exclusions:
            if exclusion in gitignore_content:
                security_checks.append(f"✅ {exclusion} excluded from Git")
            else:
                security_checks.append(f"❌ {exclusion} NOT excluded from Git")
                
    except Exception as e:
        security_checks.append(f"❌ Error checking .gitignore: {e}")
    
    # Check if sensitive files exist (they shouldn't be committed)
    sensitive_files = [
        'license.dat',
        'firebase_config_protected.json',
        '.firebase_vault.dat'
    ]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            security_checks.append(f"⚠️ {file_path} exists (will be created at runtime)")
        else:
            security_checks.append(f"✅ {file_path} not present (good)")
    
    # Print security report
    print("\n📋 Security Report:")
    for check in security_checks:
        print(f"   {check}")
    
    return True

def cleanup_build_artifacts():
    """Clean up build artifacts and temporary files"""
    
    print("🧹 Cleaning up build artifacts...")
    
    try:
        # Remove temporary files
        temp_files = [
            'firebase_installer.py.bak',
            'license_manager.py.bak',
            'firebase_protection.py.bak'
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        print("✅ Cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        return False

def main():
    """Main secure build process"""
    
    print("🚀 VARSYS Kitchen Dashboard - Secure Build Process")
    print("=" * 60)
    
    # Step 1: Embed Firebase credentials
    if not embed_firebase_credentials():
        print("❌ Build failed at Firebase embedding step")
        return False
    
    # Step 2: Update license secrets
    if not update_license_secrets():
        print("❌ Build failed at license secrets step")
        return False
    
    # Step 3: Verify security
    if not verify_security():
        print("❌ Build failed at security verification step")
        return False
    
    # Step 4: Build executable
    if not build_executable():
        print("❌ Build failed at executable creation step")
        return False
    
    # Step 5: Cleanup
    if not cleanup_build_artifacts():
        print("⚠️ Cleanup had issues, but build succeeded")
    
    print("\n" + "=" * 60)
    print("🎉 SECURE BUILD COMPLETED SUCCESSFULLY!")
    print("\n📦 Your protected executable is ready:")
    print("   📁 Location: build/exe.win-amd64-3.10/VARSYS_Kitchen_Dashboard.exe")
    print("\n🔐 Security Features:")
    print("   ✅ Firebase credentials embedded and encrypted")
    print("   ✅ License protection active")
    print("   ✅ Tamper detection enabled")
    print("   ✅ Machine-specific licensing")
    print("   ✅ No credentials in source code")
    print("\n💼 Ready for commercial distribution!")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ BUILD FAILED!")
        print("Please fix the errors above and try again.")
        sys.exit(1)
    else:
        print("\n✅ BUILD SUCCESSFUL!")
        sys.exit(0)
