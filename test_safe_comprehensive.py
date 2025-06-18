#!/usr/bin/env python3
"""
Test the safe comprehensive test suite
"""

import sys
import os
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_safe_comprehensive():
    """Test the safe comprehensive test suite"""
    print("🧪 Testing Safe Comprehensive Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        # Initialize Qt Application
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print("✅ Qt Application initialized")
        
        # Import the safe comprehensive test suite
        print("\n📦 Importing safe comprehensive test suite...")
        try:
            from safe_comprehensive_test import SafeComprehensiveTestSuite, show_safe_comprehensive_test_suite
            print("✅ Safe comprehensive test suite imported successfully")
        except Exception as e:
            print(f"❌ Failed to import safe comprehensive test suite: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Create a mock app object for testing
        class MockApp:
            def __init__(self):
                import pandas as pd
                self.data = {
                    'inventory': pd.DataFrame({'item_name': ['Test'], 'quantity': [1]}),
                    'sales': pd.DataFrame({'item': ['Test'], 'amount': [100]}),
                    'cleaning_maintenance': pd.DataFrame({'task_name': ['Test'], 'frequency': ['Daily']}),
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
                    'meal_plan': pd.DataFrame({'day': ['Monday'], 'meal_type': ['Breakfast'], 'recipe_name': ['Oatmeal'], 'servings': [2]}),
                    'recipes': pd.DataFrame({'recipe_id': [1], 'recipe_name': ['Test Recipe'], 'category': ['Main'], 'servings': [4]}),
                    'budget': pd.DataFrame({'category': ['Test'], 'amount': [1000], 'period': ['Monthly']}),
                    'items': pd.DataFrame({'item_name': ['Test'], 'category': ['Test']}),
                    'categories': pd.DataFrame({'category_name': ['Test'], 'type': ['ingredient']}),
                    'recipe_ingredients': pd.DataFrame({'recipe_id': [1], 'item_name': ['Test'], 'quantity': [100], 'unit': ['g']}),
                    'pricing': pd.DataFrame({'item_name': ['Test'], 'price': [10]}),
                    'settings': {'currency': '₹'}
                }
                
                # Mock methods
                self.central_widget = True
                self.sidebar = True
                self.content_widget = True
                self.logger = self
                
            def load_data(self):
                return self.data
                
            def info(self, msg):
                print(f"INFO: {msg}")
                
            def error(self, msg):
                print(f"ERROR: {msg}")
                
            def warning(self, msg):
                print(f"WARNING: {msg}")
        
        mock_app = MockApp()
        print("✅ Mock app created")
        
        # Test creating the safe test suite
        print("\n🔧 Creating safe comprehensive test suite...")
        try:
            test_suite = SafeComprehensiveTestSuite(mock_app)
            print("✅ Safe comprehensive test suite created successfully")
            print(f"   Type: {type(test_suite)}")
        except Exception as e:
            print(f"❌ Failed to create safe test suite: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test the show function
        print("\n🔧 Testing show function...")
        try:
            test_suite_from_show = show_safe_comprehensive_test_suite(mock_app)
            if test_suite_from_show is not None:
                print("✅ Show function works correctly")
                test_suite_from_show.close()  # Close the dialog
            else:
                print("❌ Show function returned None")
                return False
        except Exception as e:
            print(f"❌ Show function failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🏁 Safe comprehensive test suite test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_safe_comprehensive()
        if success:
            print("\n✅ Safe comprehensive test suite is working correctly!")
        else:
            print("\n❌ Safe comprehensive test suite has issues.")
    except Exception as e:
        print(f"\n💥 Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
