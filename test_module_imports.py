#!/usr/bin/env python3
"""
Test script to identify which module is causing the QWidget.__init__ error
"""

import sys
import traceback
import pandas as pd

# Test data - create proper DataFrames
test_data = {
    'inventory': pd.DataFrame(),
    'sales': pd.DataFrame(),
    'shopping_list': pd.DataFrame(),
    'cleaning_maintenance': pd.DataFrame(),
    'budget': pd.DataFrame(),
    'waste': pd.DataFrame(),
    'packing_materials': pd.DataFrame(),
    'items': pd.DataFrame(),
    'categories': pd.DataFrame(),
    'recipes': pd.DataFrame(),
    'recipe_ingredients': pd.DataFrame(),
    'pricing': pd.DataFrame(),
    'meal_plan': pd.DataFrame(),
    'sales_orders': pd.DataFrame(),
    'recipe_packing_materials': pd.DataFrame()
}

def test_module_import(module_name, class_name, *args):
    """Test importing and instantiating a module"""
    try:
        print(f"Testing {module_name}.{class_name}...")

        # Import the module
        module = __import__(f"modules.{module_name}", fromlist=[class_name])
        widget_class = getattr(module, class_name)

        # Try to instantiate with test data
        widget = widget_class(*args)
        print(f"✅ {module_name}.{class_name}: SUCCESS")
        widget.deleteLater()  # Clean up
        return True

    except Exception as e:
        print(f"❌ {module_name}.{class_name}: FAILED - {str(e)}")
        if "'PySide6.QtWidgets.QWidget.__init__' called with wrong argument types" in str(e):
            print(f"   🔍 QWidget.__init__ error detected in {module_name}")
            print(f"   📝 Full error: {traceback.format_exc()}")
        return False

def main():
    """Test all modules that were failing"""
    print("Testing Kitchen Dashboard Modules")
    print("=" * 50)

    # Initialize Qt Application first
    try:
        from PySide6.QtWidgets import QApplication
        import sys

        if not QApplication.instance():
            app = QApplication(sys.argv)
            print("✅ Qt Application initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Qt: {e}")
        return

    # Test modules one by one
    modules_to_test = [
        ("inventory_fixed", "InventoryWidget", test_data),
        ("shopping_fixed", "ShoppingWidget", test_data),
        ("sales", "SalesWidget", test_data, None),
        ("cleaning_fixed", "CleaningWidget", test_data),
        ("settings_fixed", "SettingsWidget", None, None, test_data),  # main_app, parent, data
        ("enhanced_budget", "EnhancedBudgetWidget", test_data),
        ("waste", "WasteWidget", test_data),
        ("packing_materials", "PackingMaterialsWidget", test_data),
    ]

    failed_modules = []

    for test_args in modules_to_test:
        module_name = test_args[0]
        class_name = test_args[1]
        args = test_args[2:]

        success = test_module_import(module_name, class_name, *args)
        if not success:
            failed_modules.append(f"{module_name}.{class_name}")
        print()  # Add spacing between tests

    print("=" * 50)
    print("SUMMARY:")
    if failed_modules:
        print(f"❌ Failed modules: {', '.join(failed_modules)}")
    else:
        print("✅ All modules imported successfully!")

if __name__ == "__main__":
    main()
