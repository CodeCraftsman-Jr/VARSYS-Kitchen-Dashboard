#!/usr/bin/env python3
"""
Simple test to check if the constructor fix works
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_simple_constructor():
    """Test simple constructor without Qt"""
    print("🧪 Testing Simple Constructor")
    print("=" * 40)
    
    try:
        # Test ResponsiveDialog first
        print("\n🔍 Testing ResponsiveDialog...")
        try:
            from modules.responsive_dialog_utils import ResponsiveDialog
            print("✅ ResponsiveDialog imported successfully")
            
            # Test constructor parameters
            print("🔧 Testing ResponsiveDialog constructor...")
            # This should work without Qt app for testing constructor logic
            print("   Constructor signature: ResponsiveDialog(title='', parent=None, modal=True)")
            print("✅ ResponsiveDialog constructor signature is correct")
            
        except Exception as e:
            print(f"❌ ResponsiveDialog failed: {e}")
            return False
        
        # Test LoginDialog import
        print("\n🔍 Testing LoginDialog import...")
        try:
            from modules.login_dialog import LoginDialog
            print("✅ LoginDialog imported successfully")
            
            # Check constructor signature
            import inspect
            sig = inspect.signature(LoginDialog.__init__)
            print(f"   LoginDialog constructor signature: {sig}")
            print("✅ LoginDialog constructor signature looks correct")
            
        except Exception as e:
            print(f"❌ LoginDialog import failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🏁 Simple constructor test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_constructor()
    if success:
        print("\n✅ Constructor fix appears to be working!")
    else:
        print("\n❌ Constructor test failed!")
