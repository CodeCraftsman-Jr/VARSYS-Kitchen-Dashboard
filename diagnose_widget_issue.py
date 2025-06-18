#!/usr/bin/env python3
"""
Diagnostic script to identify the QWidget constructor issue
"""

import sys
import os
import pandas as pd

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))

def test_individual_widgets():
    """Test each widget individually to find the problematic one"""
    print("🔍 Diagnosing Widget Constructor Issues")
    print("=" * 60)
    
    # Create minimal test data
    test_data = {
        'inventory': pd.DataFrame({'item_name': ['Test'], 'quantity': [10]}),
        'sales': pd.DataFrame({'item': ['Test'], 'amount': [100]}),
        'cleaning_maintenance': pd.DataFrame({'task_name': ['Test'], 'frequency': ['Daily']}),
        'waste': pd.DataFrame({'item_name': ['Test'], 'quantity': [1]}),
        'packing_materials': pd.DataFrame({'material_name': ['Test'], 'cost': [5]}),
        'settings': {'currency': '₹'}
    }
    
    # Test widgets one by one
    widgets_to_test = [
        {
            'name': 'InventoryWidget',
            'module': 'modules.inventory_fixed',
            'class_name': 'InventoryWidget',
            'constructor': lambda cls: cls(test_data)
        },
        {
            'name': 'SalesWidget', 
            'module': 'modules.sales',
            'class_name': 'SalesWidget',
            'constructor': lambda cls: cls(test_data, None)
        },
        {
            'name': 'CleaningWidget',
            'module': 'modules.cleaning_fixed', 
            'class_name': 'CleaningWidget',
            'constructor': lambda cls: cls(test_data)
        },
        {
            'name': 'SettingsWidget',
            'module': 'modules.settings_fixed',
            'class_name': 'SettingsWidget', 
            'constructor': lambda cls: cls(main_app=None, parent=None, data=test_data)
        },
        {
            'name': 'WasteWidget',
            'module': 'modules.waste',
            'class_name': 'WasteWidget',
            'constructor': lambda cls: cls(test_data)
        },
        {
            'name': 'PackingMaterialsWidget',
            'module': 'modules.packing_materials',
            'class_name': 'PackingMaterialsWidget',
            'constructor': lambda cls: cls(test_data)
        },
        {
            'name': 'ShoppingWidget',
            'module': 'modules.shopping_fixed',
            'class_name': 'ShoppingWidget',
            'constructor': lambda cls: cls(test_data)
        }
    ]
    
    failed_widgets = []
    
    for widget_info in widgets_to_test:
        print(f"\n🧪 Testing {widget_info['name']}...")
        
        try:
            # Import the module
            print(f"   📦 Importing {widget_info['module']}...")
            module = __import__(widget_info['module'], fromlist=[widget_info['class_name']])
            widget_class = getattr(module, widget_info['class_name'])
            print(f"   ✅ Import successful")
            
            # Create the widget
            print(f"   🔧 Creating widget instance...")
            widget = widget_info['constructor'](widget_class)
            print(f"   ✅ Widget created successfully")
            print(f"   📋 Type: {type(widget)}")
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed_widgets.append(widget_info['name'])
            
            # Print detailed error info
            import traceback
            print(f"   📋 Full error traceback:")
            traceback.print_exc()
            print()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if failed_widgets:
        print(f"❌ Failed widgets: {', '.join(failed_widgets)}")
        print("\nThe issue is likely in one of these widgets.")
        print("Check their constructor calls to super().__init__()")
    else:
        print("✅ All widgets created successfully!")
        print("The issue might be elsewhere in the application.")
    
    return len(failed_widgets) == 0

if __name__ == "__main__":
    try:
        # Initialize Qt first
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("✅ Qt Application initialized")
        
        # Run the diagnostic
        success = test_individual_widgets()
        
        if success:
            print("\n🎉 All widgets passed the diagnostic test!")
        else:
            print("\n⚠️  Some widgets failed. Check the output above for details.")
            
    except Exception as e:
        print(f"❌ Critical error during diagnostic: {e}")
        import traceback
        traceback.print_exc()
