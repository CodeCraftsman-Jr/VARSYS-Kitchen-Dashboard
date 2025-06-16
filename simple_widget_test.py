#!/usr/bin/env python3
"""
Simple test to isolate the QWidget constructor issue
"""

import sys
import os
import pandas as pd

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_simple_widget_creation():
    """Test simple widget creation"""
    print("🧪 Simple Widget Test")
    print("=" * 40)
    
    try:
        # Initialize Qt
        from PySide6.QtWidgets import QApplication, QWidget
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("✅ Qt initialized")
        
        # Create test data
        test_data = {
            'inventory': pd.DataFrame({'item_name': ['Test'], 'quantity': [10]}),
            'sales': pd.DataFrame({'item': ['Test'], 'amount': [100]}),
        }
        print("✅ Test data created")
        
        # Test 1: Try to import InventoryWidget
        print("\n🔍 Testing InventoryWidget import...")
        try:
            from modules.inventory_fixed import InventoryWidget
            print("✅ InventoryWidget imported successfully")
            
            # Test constructor
            print("🔧 Creating InventoryWidget...")
            widget = InventoryWidget(test_data)
            print("✅ InventoryWidget created successfully!")
            print(f"   Type: {type(widget)}")
            
        except Exception as e:
            print(f"❌ InventoryWidget failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Try to import SalesWidget
        print("\n🔍 Testing SalesWidget import...")
        try:
            from modules.sales import SalesWidget
            print("✅ SalesWidget imported successfully")
            
            # Test constructor
            print("🔧 Creating SalesWidget...")
            widget = SalesWidget(test_data, None)
            print("✅ SalesWidget created successfully!")
            print(f"   Type: {type(widget)}")
            
        except Exception as e:
            print(f"❌ SalesWidget failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🏁 Simple test completed!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_widget_creation()
