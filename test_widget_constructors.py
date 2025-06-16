#!/usr/bin/env python3
"""
Test script to identify QWidget constructor issues
"""

import sys
import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget

def test_widget_constructors():
    """Test widget constructors to identify the issue"""
    
    # Create test data
    test_data = {
        'inventory': pd.DataFrame({
            'item_id': [1, 2, 3],
            'item_name': ['Test Item 1', 'Test Item 2', 'Test Item 3'],
            'category': ['Category A', 'Category B', 'Category A'],
            'quantity': [10, 20, 15],
            'unit': ['kg', 'pcs', 'liters']
        }),
        'shopping_list': pd.DataFrame({
            'item_id': [1, 2],
            'item_name': ['Shopping Item 1', 'Shopping Item 2'],
            'category': ['Category A', 'Category B'],
            'quantity': [5, 10],
            'unit': ['kg', 'pcs'],
            'priority': ['High', 'Medium'],
            'status': ['Pending', 'Pending']
        }),
        'pricing': pd.DataFrame({
            'recipe_id': [1, 2],
            'recipe_name': ['Recipe 1', 'Recipe 2'],
            'cost_of_making': [10.0, 15.0],
            'others_pricing': [20.0, 25.0],
            'our_pricing': [18.0, 22.0]
        })
    }
    
    print("🧪 Testing Widget Constructors...")
    print(f"Test data keys: {list(test_data.keys())}")
    
    # Test 1: Inventory Widget
    print("\n1️⃣ Testing InventoryWidget...")
    try:
        from modules.inventory_fixed import InventoryWidget
        print("✅ InventoryWidget imported successfully")
        
        # Test constructor
        inventory_widget = InventoryWidget(test_data)
        print("✅ InventoryWidget created successfully")
        print(f"   Widget type: {type(inventory_widget)}")
        print(f"   Is QWidget: {isinstance(inventory_widget, QWidget)}")
        
    except Exception as e:
        print(f"❌ InventoryWidget failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Shopping Widget
    print("\n2️⃣ Testing ShoppingWidget...")
    try:
        from modules.shopping_fixed import ShoppingWidget
        print("✅ ShoppingWidget imported successfully")
        
        # Test constructor
        shopping_widget = ShoppingWidget(test_data)
        print("✅ ShoppingWidget created successfully")
        print(f"   Widget type: {type(shopping_widget)}")
        print(f"   Is QWidget: {isinstance(shopping_widget, QWidget)}")
        
    except Exception as e:
        print(f"❌ ShoppingWidget failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Pricing Widget
    print("\n3️⃣ Testing PricingManagementWidget...")
    try:
        from modules.pricing_management import PricingManagementWidget
        print("✅ PricingManagementWidget imported successfully")

        # Test constructor
        pricing_widget = PricingManagementWidget(test_data)
        print("✅ PricingManagementWidget created successfully")
        print(f"   Widget type: {type(pricing_widget)}")
        print(f"   Is QWidget: {isinstance(pricing_widget, QWidget)}")

    except Exception as e:
        print(f"❌ PricingManagementWidget failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Sales Widget
    print("\n4️⃣ Testing SalesWidget...")
    try:
        from modules.sales import SalesWidget
        print("✅ SalesWidget imported successfully")

        # Test constructor
        sales_widget = SalesWidget(test_data, None)  # data, inventory_widget
        print("✅ SalesWidget created successfully")
        print(f"   Widget type: {type(sales_widget)}")
        print(f"   Is QWidget: {isinstance(sales_widget, QWidget)}")

    except Exception as e:
        print(f"❌ SalesWidget failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 5: Cleaning Widget
    print("\n5️⃣ Testing CleaningWidget...")
    try:
        from modules.cleaning_fixed import CleaningWidget
        print("✅ CleaningWidget imported successfully")

        # Test constructor
        cleaning_widget = CleaningWidget(test_data)
        print("✅ CleaningWidget created successfully")
        print(f"   Widget type: {type(cleaning_widget)}")
        print(f"   Is QWidget: {isinstance(cleaning_widget, QWidget)}")

    except Exception as e:
        print(f"❌ CleaningWidget failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 6: Settings Widget
    print("\n6️⃣ Testing SettingsWidget...")
    try:
        from modules.settings_fixed import SettingsWidget
        print("✅ SettingsWidget imported successfully")

        # Test constructor
        settings_widget = SettingsWidget(main_app=None, parent=None, data=test_data)
        print("✅ SettingsWidget created successfully")
        print(f"   Widget type: {type(settings_widget)}")
        print(f"   Is QWidget: {isinstance(settings_widget, QWidget)}")

    except Exception as e:
        print(f"❌ SettingsWidget failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 7: Waste Widget
    print("\n7️⃣ Testing WasteWidget...")
    try:
        from modules.waste import WasteWidget
        print("✅ WasteWidget imported successfully")

        # Test constructor
        waste_widget = WasteWidget(test_data)
        print("✅ WasteWidget created successfully")
        print(f"   Widget type: {type(waste_widget)}")
        print(f"   Is QWidget: {isinstance(waste_widget, QWidget)}")

    except Exception as e:
        print(f"❌ WasteWidget failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 8: Packing Materials Widget
    print("\n8️⃣ Testing PackingMaterialsWidget...")
    try:
        from modules.packing_materials import PackingMaterialsWidget
        print("✅ PackingMaterialsWidget imported successfully")

        # Test constructor
        packing_widget = PackingMaterialsWidget(test_data)
        print("✅ PackingMaterialsWidget created successfully")
        print(f"   Widget type: {type(packing_widget)}")
        print(f"   Is QWidget: {isinstance(packing_widget, QWidget)}")

    except Exception as e:
        print(f"❌ PackingMaterialsWidget failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n🏁 Constructor testing completed!")

if __name__ == "__main__":
    # Create QApplication for widget testing
    app = QApplication(sys.argv)
    
    try:
        test_widget_constructors()
    except Exception as e:
        print(f"❌ Test script failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test script completed!")
