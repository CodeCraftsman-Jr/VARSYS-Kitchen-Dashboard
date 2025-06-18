#!/usr/bin/env python3
"""
Test specific widgets to identify the QWidget constructor issue
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))

def test_widget_creation():
    """Test widget creation to identify the problematic widget"""
    print("🧪 Testing Widget Creation")
    print("=" * 50)
    
    # Initialize Qt Application
    try:
        from PySide6.QtWidgets import QApplication, QWidget
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("✅ Qt Application initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Qt: {e}")
        return False
    
    # Create test data
    test_data = {
        'inventory': pd.DataFrame({'item_name': ['Test Item'], 'quantity': [10]}),
        'sales': pd.DataFrame({'item': ['Test'], 'amount': [100]}),
        'cleaning_maintenance': pd.DataFrame({'task_name': ['Test Task'], 'frequency': ['Daily']}),
        'waste': pd.DataFrame({'item_name': ['Test'], 'quantity': [1]}),
        'packing_materials': pd.DataFrame({'material_name': ['Test'], 'cost': [5]}),
        'settings': {'currency': '₹'}
    }
    print("✅ Test data created")
    
    # Test each widget individually
    widgets_to_test = [
        ('InventoryWidget', 'modules.inventory_fixed', lambda: InventoryWidget(test_data)),
        ('SalesWidget', 'modules.sales', lambda: SalesWidget(test_data, None)),
        ('CleaningWidget', 'modules.cleaning_fixed', lambda: CleaningWidget(test_data)),
        ('SettingsWidget', 'modules.settings_fixed', lambda: SettingsWidget(main_app=None, parent=None, data=test_data)),
        ('WasteWidget', 'modules.waste', lambda: WasteWidget(test_data)),
        ('PackingMaterialsWidget', 'modules.packing_materials', lambda: PackingMaterialsWidget(test_data)),
        ('ShoppingWidget', 'modules.shopping_fixed', lambda: ShoppingWidget(test_data)),
    ]
    
    for widget_name, module_name, widget_creator in widgets_to_test:
        print(f"\n🔍 Testing {widget_name}...")
        try:
            # Import the module
            module = __import__(module_name, fromlist=[widget_name])
            widget_class = getattr(module, widget_name)
            print(f"   ✅ {widget_name} imported successfully")
            
            # Create the widget
            widget = widget_creator()
            print(f"   ✅ {widget_name} created successfully")
            print(f"   📋 Type: {type(widget)}")
            print(f"   📋 Is QWidget: {isinstance(widget, QWidget)}")
            
        except Exception as e:
            print(f"   ❌ {widget_name} failed: {e}")
            import traceback
            print(f"   📋 Full error:")
            traceback.print_exc()
            print()
    
    print("\n🏁 Widget testing completed!")
    return True

if __name__ == "__main__":
    test_widget_creation()
