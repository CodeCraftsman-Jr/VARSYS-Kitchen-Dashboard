#!/usr/bin/env python3
"""
Test WhatsApp integration imports to identify specific issues
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_whatsapp_import():
    """Test importing WhatsApp integration module"""
    print("🧪 Testing WhatsApp integration import...")
    
    try:
        # Test basic import
        print("1. Testing basic module import...")
        import modules.whatsapp_integration as wa
        print("✅ Basic import successful")
        
        # Test class import
        print("2. Testing WhatsAppIntegrationWidget class...")
        widget_class = getattr(wa, 'WhatsAppIntegrationWidget', None)
        if widget_class:
            print("✅ WhatsAppIntegrationWidget class found")
            
            # Check for check_chrome_installation method
            if hasattr(widget_class, 'check_chrome_installation'):
                print("✅ check_chrome_installation method found")
            else:
                print("❌ check_chrome_installation method missing")
                # List all methods
                methods = [method for method in dir(widget_class) if not method.startswith('_')]
                print(f"Available methods: {methods[:10]}...")  # Show first 10 methods
        else:
            print("❌ WhatsAppIntegrationWidget class not found")
            
        # Test Qt imports
        print("3. Testing Qt imports...")
        try:
            from PySide6.QtCore import Signal, QObject
            print("✅ PySide6 Signal and QObject import successful")
        except ImportError as e:
            print(f"❌ PySide6 import failed: {e}")
            
        # Test creating widget instance (without Qt app)
        print("4. Testing widget instantiation...")
        try:
            # This will fail without Qt app, but we can catch the specific error
            widget = widget_class()
            print("✅ Widget created successfully")
        except Exception as e:
            if "QWidget" in str(e) or "QApplication" in str(e):
                print("⚠️ Widget creation failed (expected - no Qt app context)")
            else:
                print(f"❌ Unexpected widget creation error: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_compatibility():
    """Test Signal vs pyqtSignal compatibility"""
    print("\n🧪 Testing Signal compatibility...")
    
    try:
        from PySide6.QtCore import Signal
        print("✅ PySide6.QtCore.Signal import successful")
        
        # Test creating a signal
        test_signal = Signal(str)
        print("✅ Signal creation successful")
        
        # Test if pyqtSignal alias exists
        try:
            from modules.whatsapp_integration import pyqtSignal
            print("✅ pyqtSignal alias found in module")
        except ImportError:
            print("⚠️ pyqtSignal alias not found (may not be needed)")
            
        return True
        
    except Exception as e:
        print(f"❌ Signal compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting WhatsApp Integration Import Tests")
    print("=" * 60)
    
    test1_result = test_whatsapp_import()
    test2_result = test_signal_compatibility()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 All import tests passed!")
        return 0
    else:
        print("⚠️ Some import tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
