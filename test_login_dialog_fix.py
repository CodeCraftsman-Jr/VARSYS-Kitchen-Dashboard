#!/usr/bin/env python3
"""
Test the LoginDialog fix
"""

import sys
import os
import pandas as pd

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_login_dialog_fix():
    """Test that the LoginDialog constructor fix works"""
    print("🧪 Testing LoginDialog Fix")
    print("=" * 40)
    
    try:
        # Initialize Qt
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("✅ Qt initialized")
        
        # Test LoginDialog import and creation
        print("\n🔍 Testing LoginDialog...")
        try:
            from modules.login_dialog import LoginDialog
            print("✅ LoginDialog imported successfully")
            
            # Test constructor
            print("🔧 Creating LoginDialog...")
            dialog = LoginDialog()
            print("✅ LoginDialog created successfully!")
            print(f"   Type: {type(dialog)}")
            
        except Exception as e:
            print(f"❌ LoginDialog failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🏁 LoginDialog fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_login_dialog_fix()
    if success:
        print("\n✅ LoginDialog fix is working correctly!")
    else:
        print("\n❌ LoginDialog fix test failed!")
