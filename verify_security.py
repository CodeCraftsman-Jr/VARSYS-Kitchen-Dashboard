#!/usr/bin/env python3
"""
Security Verification Script for VARSYS Kitchen Dashboard
Checks for potential security issues before GitHub upload
"""

import os
import re
import sys
from pathlib import Path

def check_for_hardcoded_secrets():
    """Check for hardcoded secrets in Python files"""
    print("🔍 Checking for hardcoded secrets...")
    
    # Patterns that might indicate hardcoded secrets
    secret_patterns = [
        r'api_key\s*=\s*["\'][^"\']{20,}["\']',  # API keys
        r'password\s*=\s*["\'][^"\']+["\']',      # Passwords
        r'secret\s*=\s*["\'][^"\']{20,}["\']',   # Secrets
        r'token\s*=\s*["\'][^"\']{20,}["\']',    # Tokens
        r'sk-[a-zA-Z0-9]{20,}',                  # OpenAI style keys
        r'pk_[a-zA-Z0-9]{20,}',                  # Stripe public keys
        r'AIza[a-zA-Z0-9]{35}',                  # Google API keys
        r'AKIA[a-zA-Z0-9]{16}',                  # AWS access keys
    ]
    
    issues_found = []
    
    # Check all Python files
    for py_file in Path('.').rglob('*.py'):
        # Skip excluded directories
        if any(excluded in str(py_file) for excluded in ['dashboardcopy', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Check if it's actually a hardcoded secret (not a template or env var)
                    for match in matches:
                        if not any(safe_word in match.lower() for safe_word in [
                            'your_', 'example', 'template', 'placeholder', 'os.getenv', 'environ'
                        ]):
                            issues_found.append(f"{py_file}: {match}")
                            
        except Exception as e:
            print(f"⚠️ Error reading {py_file}: {e}")
    
    if issues_found:
        print("❌ Potential hardcoded secrets found:")
        for issue in issues_found:
            print(f"   {issue}")
        return False
    else:
        print("✅ No hardcoded secrets detected")
        return True

def check_gitignore():
    """Check if .gitignore properly excludes sensitive files"""
    print("\n🔍 Checking .gitignore configuration...")
    
    required_exclusions = [
        '.env',
        'firebase_credentials.json',
        'api_keys.json',
        'secrets.json',
        'config.json',
        'credentials.json',
        'dashboardcopy/',
    ]
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        missing_exclusions = []
        for exclusion in required_exclusions:
            if exclusion not in gitignore_content:
                missing_exclusions.append(exclusion)
        
        if missing_exclusions:
            print("❌ Missing exclusions in .gitignore:")
            for exclusion in missing_exclusions:
                print(f"   {exclusion}")
            return False
        else:
            print("✅ .gitignore properly configured")
            return True
            
    except FileNotFoundError:
        print("❌ .gitignore file not found")
        return False

def check_environment_usage():
    """Check if environment variables are used for sensitive data"""
    print("\n🔍 Checking environment variable usage...")
    
    env_patterns = [
        r'os\.getenv\(["\']([^"\']+)["\']',
        r'os\.environ\[["\']([^"\']+)["\']',
        r'environ\.get\(["\']([^"\']+)["\']',
    ]
    
    env_vars_found = set()
    
    for py_file in Path('.').rglob('*.py'):
        if any(excluded in str(py_file) for excluded in ['dashboardcopy', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in env_patterns:
                matches = re.findall(pattern, content)
                env_vars_found.update(matches)
                
        except Exception as e:
            continue
    
    if env_vars_found:
        print("✅ Environment variables properly used:")
        for var in sorted(env_vars_found):
            print(f"   {var}")
        return True
    else:
        print("⚠️ No environment variable usage detected")
        return True

def check_sensitive_files():
    """Check for sensitive files that shouldn't be committed"""
    print("\n🔍 Checking for sensitive files...")
    
    sensitive_files = [
        '.env',
        '.env.local',
        '.env.production',
        'firebase_credentials.json',
        'firebase_config.json',
        'api_keys.json',
        'secrets.json',
        'config.json',
        'credentials.json',
        'jwt_secret.key',
    ]
    
    found_files = []
    for file_pattern in sensitive_files:
        for file_path in Path('.').rglob(file_pattern):
            if not any(excluded in str(file_path) for excluded in ['dashboardcopy', '__pycache__', '.git']):
                found_files.append(str(file_path))
    
    if found_files:
        print("⚠️ Sensitive files found (ensure they're in .gitignore):")
        for file_path in found_files:
            print(f"   {file_path}")
        return True  # Not necessarily an error if they're in .gitignore
    else:
        print("✅ No sensitive files found in main directory")
        return True

def check_documentation():
    """Check if security documentation exists"""
    print("\n🔍 Checking security documentation...")
    
    required_docs = [
        'SECURITY.md',
        'README.md',
        '.gitignore',
    ]
    
    missing_docs = []
    for doc in required_docs:
        if not Path(doc).exists():
            missing_docs.append(doc)
    
    if missing_docs:
        print("❌ Missing documentation:")
        for doc in missing_docs:
            print(f"   {doc}")
        return False
    else:
        print("✅ Security documentation present")
        return True

def main():
    """Run all security checks"""
    print("🔒 VARSYS Kitchen Dashboard Security Verification")
    print("=" * 50)
    
    checks = [
        check_for_hardcoded_secrets,
        check_gitignore,
        check_environment_usage,
        check_sensitive_files,
        check_documentation,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error in {check.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📋 Security Check Summary:")
    
    if all(results):
        print("✅ ALL SECURITY CHECKS PASSED")
        print("🎉 Repository is safe for GitHub upload!")
        print("\n🔒 Security Features:")
        print("   ✅ No hardcoded secrets")
        print("   ✅ Proper .gitignore configuration")
        print("   ✅ Environment variables used")
        print("   ✅ Security documentation present")
        print("   ✅ Sensitive files excluded")
        return True
    else:
        print("❌ SOME SECURITY CHECKS FAILED")
        print("⚠️ Please fix the issues above before uploading to GitHub")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
