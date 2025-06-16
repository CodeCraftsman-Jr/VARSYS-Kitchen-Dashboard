#!/usr/bin/env python3
"""
Debug module import issues step by step
"""

import sys
import os
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))

def debug_imports():
    """Debug imports step by step"""
    print("🔍 Debugging Module Import Issues")
    print("=" * 50)
    print(f"Debug started at: {datetime.now()}")
    print()
    
    # Test basic imports first
    print("1️⃣ Testing basic Python imports...")
    try:
        import pandas as pd
        print("✅ pandas imported")
        
        from datetime import datetime
        print("✅ datetime imported")
        
        print("✅ Basic Python imports successful")
    except Exception as e:
        print(f"❌ Basic Python imports failed: {e}")
        return False
    
    # Test Qt imports
    print("\n2️⃣ Testing Qt imports...")
    try:
        from PySide6.QtWidgets import QApplication, QWidget
        print("✅ PySide6.QtWidgets imported")
        
        from PySide6.QtCore import Qt, Signal
        print("✅ PySide6.QtCore imported")
        
        from PySide6.QtGui import QFont
        print("✅ PySide6.QtGui imported")
        
        print("✅ Qt imports successful")
    except Exception as e:
        print(f"❌ Qt imports failed: {e}")
        return False
    
    # Test Qt Application creation
    print("\n3️⃣ Testing Qt Application creation...")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("✅ Qt Application created")
    except Exception as e:
        print(f"❌ Qt Application creation failed: {e}")
        return False
    
    # Test individual module imports
    print("\n4️⃣ Testing individual module imports...")
    
    modules_to_test = [
        ('inventory_fixed', 'modules.inventory_fixed'),
        ('sales', 'modules.sales'),
        ('shopping_fixed', 'modules.shopping_fixed'),
        ('cleaning_fixed', 'modules.cleaning_fixed'),
        ('settings_fixed', 'modules.settings_fixed'),
        ('waste', 'modules.waste'),
        ('packing_materials', 'modules.packing_materials'),
        ('pricing_management', 'modules.pricing_management'),
        ('firebase_sync', 'modules.firebase_sync'),
        ('login_dialog', 'modules.login_dialog')
    ]
    
    failed_imports = []
    successful_imports = []
    
    for module_name, module_path in modules_to_test:
        print(f"   📦 Testing {module_name}...")
        try:
            module = __import__(module_path, fromlist=[''])
            print(f"   ✅ {module_name} imported successfully")
            successful_imports.append(module_name)
        except Exception as e:
            print(f"   ❌ {module_name} failed: {e}")
            failed_imports.append((module_name, str(e)))
    
    # Test widget class imports
    print("\n5️⃣ Testing widget class imports...")
    
    widget_tests = [
        ('InventoryWidget', 'modules.inventory_fixed', 'InventoryWidget'),
        ('SalesWidget', 'modules.sales', 'SalesWidget'),
        ('ShoppingWidget', 'modules.shopping_fixed', 'ShoppingWidget'),
        ('CleaningWidget', 'modules.cleaning_fixed', 'CleaningWidget'),
        ('SettingsWidget', 'modules.settings_fixed', 'SettingsWidget'),
        ('WasteWidget', 'modules.waste', 'WasteWidget'),
        ('PackingMaterialsWidget', 'modules.packing_materials', 'PackingMaterialsWidget'),
        ('PricingManagementWidget', 'modules.pricing_management', 'PricingManagementWidget'),
        ('FirebaseSync', 'modules.firebase_sync', 'FirebaseSync'),
        ('LoginDialog', 'modules.login_dialog', 'LoginDialog')
    ]
    
    failed_widgets = []
    successful_widgets = []
    
    for widget_name, module_path, class_name in widget_tests:
        print(f"   🔧 Testing {widget_name}...")
        try:
            module = __import__(module_path, fromlist=[class_name])
            widget_class = getattr(module, class_name)
            print(f"   ✅ {widget_name} class imported successfully")
            successful_widgets.append(widget_name)
        except Exception as e:
            print(f"   ❌ {widget_name} failed: {e}")
            failed_widgets.append((widget_name, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print("=" * 50)
    
    print(f"✅ Successful module imports: {len(successful_imports)}")
    for module in successful_imports:
        print(f"   • {module}")
    
    print(f"\n❌ Failed module imports: {len(failed_imports)}")
    for module, error in failed_imports:
        print(f"   • {module}: {error}")
    
    print(f"\n✅ Successful widget imports: {len(successful_widgets)}")
    for widget in successful_widgets:
        print(f"   • {widget}")
    
    print(f"\n❌ Failed widget imports: {len(failed_widgets)}")
    for widget, error in failed_widgets:
        print(f"   • {widget}: {error}")
    
    # Test simple widget creation (only for successful imports)
    print("\n6️⃣ Testing simple widget creation...")
    
    # Create minimal test data
    test_data = {
        'inventory': pd.DataFrame({'item_name': ['Test'], 'quantity': [1]}),
        'sales': pd.DataFrame({'item': ['Test'], 'amount': [100]}),
        'waste': pd.DataFrame({
            'item_name': ['Test'], 
            'quantity': [1], 
            'reason': ['Spoiled'], 
            'cost': [10.0],
            'unit': ['kg'],
            'date': ['2024-01-01']
        }),
        'settings': {'currency': '₹'}
    }
    
    creation_tests = [
        ('InventoryWidget', 'modules.inventory_fixed', 'InventoryWidget', (test_data,)),
        ('SalesWidget', 'modules.sales', 'SalesWidget', (test_data, None)),
        ('WasteWidget', 'modules.waste', 'WasteWidget', (test_data,))
    ]
    
    for widget_name, module_path, class_name, args in creation_tests:
        if widget_name in successful_widgets:
            print(f"   🏗️ Testing {widget_name} creation...")
            try:
                module = __import__(module_path, fromlist=[class_name])
                widget_class = getattr(module, class_name)
                widget = widget_class(*args)
                print(f"   ✅ {widget_name} created successfully")
            except Exception as e:
                print(f"   ❌ {widget_name} creation failed: {e}")
                import traceback
                print(f"   📋 Traceback: {traceback.format_exc()}")
    
    print("\n🏁 Debug completed!")
    
    if failed_imports or failed_widgets:
        print(f"\n⚠️ Found {len(failed_imports)} import failures and {len(failed_widgets)} widget failures")
        return False
    else:
        print("\n🎉 All imports and widgets working correctly!")
        return True

if __name__ == "__main__":
    try:
        success = debug_imports()
        if success:
            print("\n✅ All modules are working correctly!")
        else:
            print("\n❌ Some modules have issues that need to be fixed.")
    except Exception as e:
        print(f"\n💥 Critical error during debugging: {e}")
        import traceback
        traceback.print_exc()
