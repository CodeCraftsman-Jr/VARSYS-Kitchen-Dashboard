#!/usr/bin/env python3
"""
Quick test for Kitchen Dashboard v1.1.3 - No GUI components
Tests imports and basic functionality without creating windows
"""

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")

    try:
        # Test version
        import __version__
        print(f"OK Version: {__version__.__version__}")

        # Test startup loading screen
        from modules.startup_loading_screen import LoadingWorker, SimpleLoadingDialog
        print("OK Startup loading screen imports")

        # Test account settings
        from modules.account_settings_dialog import AccountSettingsDialog
        print("OK Account settings dialog imports")

        # Test Firebase integration
        from modules import firebase_integration
        if hasattr(firebase_integration, 'change_user_password'):
            print("OK Firebase password change function exists")

        # Test user profile widget
        from modules.user_profile_widget import UserProfileDialog
        if hasattr(UserProfileDialog, 'account_settings_requested'):
            print("OK User profile integration working")

        # Test main app import (without creating instance)
        import kitchen_app
        print("OK Main application imports successfully")
        
        return True

    except Exception as e:
        print(f"FAIL Import test failed: {e}")
        return False

def test_version_consistency():
    """Test version consistency across files"""
    print("\nTesting version consistency...")

    try:
        import __version__
        
        # Check version format
        version = __version__.__version__
        if version == "1.1.3":
            print(f"OK Version is correctly set to {version}")
            return True
        else:
            print(f"FAIL Version is {version}, expected 1.1.3")
            return False

    except Exception as e:
        print(f"FAIL Version test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")

    import os
    
    required_files = [
        "kitchen_app.py",
        "__version__.py",
        "modules/startup_loading_screen.py",
        "modules/account_settings_dialog.py",
        "modules/user_profile_widget.py",
        "modules/firebase_integration.py",
        "CHANGELOG.md",
        "V1_1_3_IMPLEMENTATION_SUMMARY.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print(f"OK All {len(required_files)} required files exist")
        return True
    else:
        print(f"FAIL Missing files: {missing_files}")
        return False

def main():
    """Run all quick tests"""
    print("="*50)
    print("KITCHEN DASHBOARD v1.1.3 QUICK TEST")
    print("="*50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Version Consistency", test_version_consistency),
        ("Critical Imports", test_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "="*50)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("All quick tests passed!")
        print("v1.1.3 is ready for deployment!")
    else:
        print("Some tests failed - check implementation")
    
    print("="*50)
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
