#!/usr/bin/env python3
"""
Comprehensive test for all Kitchen Dashboard modules
Tests widget creation to identify constructor issues
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

def test_all_modules():
    """Test all modules to identify issues"""
    print("🧪 Comprehensive Module Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
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
        'waste': pd.DataFrame({
            'item_name': ['Test'],
            'quantity': [1],
            'reason': ['Spoiled'],
            'cost': [10.0],
            'unit': ['kg'],
            'date': ['2024-01-01']
        }),
        'packing_materials': pd.DataFrame({'material_name': ['Test'], 'cost': [5]}),
        'shopping_list': pd.DataFrame({'item': ['Test'], 'quantity': [1]}),
        'settings': {'currency': '₹'}
    }
    print("✅ Test data created")
    
    # Test modules one by one
    modules_to_test = [
        {
            'name': 'Inventory Module',
            'module': 'modules.inventory_fixed',
            'class': 'InventoryWidget',
            'args': (test_data,)
        },
        {
            'name': 'Sales Module', 
            'module': 'modules.sales',
            'class': 'SalesWidget',
            'args': (test_data, None)
        },
        {
            'name': 'Shopping Module',
            'module': 'modules.shopping_fixed',
            'class': 'ShoppingWidget', 
            'args': (test_data,)
        },
        {
            'name': 'Cleaning Module',
            'module': 'modules.cleaning_fixed',
            'class': 'CleaningWidget',
            'args': (test_data,)
        },
        {
            'name': 'Settings Module',
            'module': 'modules.settings_fixed',
            'class': 'SettingsWidget',
            'args': (),
            'kwargs': {'main_app': None, 'parent': None, 'data': test_data}
        },
        {
            'name': 'Waste Module',
            'module': 'modules.waste',
            'class': 'WasteWidget',
            'args': (test_data,)
        },
        {
            'name': 'Packing Materials Module',
            'module': 'modules.packing_materials', 
            'class': 'PackingMaterialsWidget',
            'args': (test_data,)
        },
        {
            'name': 'Pricing Module',
            'module': 'modules.pricing_management',
            'class': 'PricingManagementWidget',
            'args': (test_data,)
        },
        {
            'name': 'Meal Planning Module',
            'module': 'modules.fixed_meal_planning',
            'class': 'FixedMealPlanningWidget',
            'args': (test_data,)
        },
        {
            'name': 'Firebase Module',
            'module': 'modules.firebase_sync',
            'class': 'FirebaseSync',
            'args': (None,)  # parent argument
        },
        {
            'name': 'Login Dialog',
            'module': 'modules.login_dialog',
            'class': 'LoginDialog',
            'args': ()
        }
    ]
    
    failed_modules = []
    passed_modules = []
    
    for module_info in modules_to_test:
        print(f"\n🔍 Testing {module_info['name']}...")
        
        try:
            # Import the module
            print(f"   📦 Importing {module_info['module']}...")
            module = __import__(module_info['module'], fromlist=[module_info['class']])
            widget_class = getattr(module, module_info['class'])
            print(f"   ✅ Import successful")
            
            # Create the widget
            print(f"   🔧 Creating {module_info['class']} instance...")
            args = module_info.get('args', ())
            kwargs = module_info.get('kwargs', {})
            
            if kwargs:
                widget = widget_class(*args, **kwargs)
            else:
                widget = widget_class(*args)
                
            print(f"   ✅ {module_info['name']}: PASSED")
            print(f"   📋 Type: {type(widget)}")
            passed_modules.append(module_info['name'])
            
        except Exception as e:
            print(f"   ❌ {module_info['name']}: FAILED - {e}")
            failed_modules.append(module_info['name'])
            
            # Print detailed error info
            import traceback
            print(f"   📋 Full error traceback:")
            traceback.print_exc()
            print()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Passed: {len(passed_modules)}")
    for module in passed_modules:
        print(f"   • {module}")
    
    print(f"\n❌ Failed: {len(failed_modules)}")
    for module in failed_modules:
        print(f"   • {module}")
    
    if failed_modules:
        print(f"\n⚠️  {len(failed_modules)} modules failed testing")
        return False
    else:
        print(f"\n🎉 All {len(passed_modules)} modules passed!")
        return True

if __name__ == "__main__":
    try:
        success = test_all_modules()
        if success:
            print("\n✅ All modules are working correctly!")
        else:
            print("\n❌ Some modules have issues that need to be fixed.")
    except Exception as e:
        print(f"\n💥 Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
