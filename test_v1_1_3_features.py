#!/usr/bin/env python3
"""
Test script for Kitchen Dashboard v1.1.3 new features
Tests account settings and startup loading screen functionality
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

def test_startup_loading_screen():
    """Test the startup loading screen"""
    print("Testing startup loading screen...")
    try:
        from modules.startup_loading_screen import show_startup_loading_screen
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        loading_screen = show_startup_loading_screen()
        
        # Auto-close after 6 seconds for testing
        def close_loading():
            loading_screen.close()
            print("✅ Startup loading screen test completed successfully")
        
        QTimer.singleShot(6000, close_loading)
        
        return True
        
    except Exception as e:
        print(f"❌ Startup loading screen test failed: {e}")
        return False

def test_account_settings_dialog():
    """Test the account settings dialog"""
    print("Testing account settings dialog...")
    try:
        from modules.account_settings_dialog import AccountSettingsDialog
        
        # Mock user info for testing
        mock_user_info = {
            'email': 'test@example.com',
            'displayName': 'Test User',
            'localId': 'test_user_id_12345',
            'login_time': '2025-06-17 10:00:00'
        }
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = AccountSettingsDialog(mock_user_info)
        
        # Test dialog creation
        if dialog.windowTitle() == "Account Settings":
            print("✅ Account settings dialog created successfully")
            dialog.close()
            return True
        else:
            print("❌ Account settings dialog title incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Account settings dialog test failed: {e}")
        return False

def test_firebase_password_change():
    """Test Firebase password change function"""
    print("Testing Firebase password change function...")
    try:
        from modules import firebase_integration
        
        # Check if the function exists
        if hasattr(firebase_integration, 'change_user_password'):
            print("✅ Firebase password change function exists")
            return True
        else:
            print("❌ Firebase password change function not found")
            return False
            
    except Exception as e:
        print(f"❌ Firebase password change test failed: {e}")
        return False

def test_version_update():
    """Test version information update"""
    print("Testing version information...")
    try:
        import __version__
        
        if __version__.__version__ == "1.1.3":
            print("✅ Version updated to 1.1.3 successfully")
            return True
        else:
            print(f"❌ Version is {__version__.__version__}, expected 1.1.3")
            return False
            
    except Exception as e:
        print(f"❌ Version test failed: {e}")
        return False

def test_user_profile_integration():
    """Test user profile widget integration"""
    print("Testing user profile widget integration...")
    try:
        from modules.user_profile_widget import UserProfileDialog
        
        # Check if account_settings_requested signal exists
        dialog_class = UserProfileDialog
        if hasattr(dialog_class, 'account_settings_requested'):
            print("✅ User profile widget integration successful")
            return True
        else:
            print("❌ User profile widget missing account_settings_requested signal")
            return False
            
    except Exception as e:
        print(f"❌ User profile integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests for v1.1.3 features"""
    print("="*60)
    print("KITCHEN DASHBOARD v1.1.3 FEATURE TESTS")
    print("="*60)
    
    tests = [
        ("Version Update", test_version_update),
        ("Firebase Password Change", test_firebase_password_change),
        ("Account Settings Dialog", test_account_settings_dialog),
        ("User Profile Integration", test_user_profile_integration),
        ("Startup Loading Screen", test_startup_loading_screen),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   Test failed: {test_name}")
        except Exception as e:
            print(f"   Test error in {test_name}: {e}")
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! v1.1.3 features are working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    try:
        # Ensure we're in the right directory
        if not os.path.exists("kitchen_app.py"):
            print("❌ Please run this script from the Kitchen Dashboard root directory")
            sys.exit(1)
        
        success = run_all_tests()
        
        # If running with GUI, show a summary dialog
        if len(sys.argv) > 1 and sys.argv[1] == "--gui":
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            if success:
                QMessageBox.information(None, "Test Results", 
                                      "🎉 All v1.1.3 features tested successfully!\n\n"
                                      "✅ Version updated to 1.1.3\n"
                                      "✅ Account settings dialog\n"
                                      "✅ Startup loading screen\n"
                                      "✅ Firebase password change\n"
                                      "✅ User profile integration")
            else:
                QMessageBox.warning(None, "Test Results", 
                                  "⚠️ Some tests failed. Please check the console output.")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
