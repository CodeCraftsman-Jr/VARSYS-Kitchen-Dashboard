#!/usr/bin/env python3
"""
Standalone test for the comprehensive test suite
"""

import sys
import os
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))
sys.path.insert(0, os.path.join(current_dir, 'tests'))

def test_comprehensive_suite():
    """Test the comprehensive test suite"""
    print("🧪 Testing Comprehensive Test Suite")
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
        
        # Import the comprehensive test suite
        print("\n📦 Importing comprehensive test suite...")
        try:
            from comprehensive_test_suite import ComprehensiveTestSuite
            print("✅ Comprehensive test suite imported successfully")
        except Exception as e:
            print(f"❌ Failed to import comprehensive test suite: {e}")
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
                    'settings': {'currency': '₹'}
                }
        
        mock_app = MockApp()
        print("✅ Mock app created")
        
        # Create test suite instance
        print("\n🔧 Creating comprehensive test suite instance...")
        try:
            test_suite = ComprehensiveTestSuite(mock_app)
            print("✅ Comprehensive test suite instance created successfully")
        except Exception as e:
            print(f"❌ Failed to create test suite instance: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test individual components (safer approach)
        print("\n🔍 Testing individual components...")
        
        test_methods = [
            'test_inventory',
            'test_sales', 
            'test_shopping',
            'test_cleaning',
            'test_settings'
        ]
        
        passed_tests = []
        failed_tests = []
        
        for test_method in test_methods:
            print(f"\n   🧪 Running {test_method}...")
            try:
                method = getattr(test_suite, test_method)
                method()
                print(f"   ✅ {test_method}: PASSED")
                passed_tests.append(test_method)
            except Exception as e:
                print(f"   ❌ {test_method}: FAILED - {e}")
                failed_tests.append(test_method)
        
        # Summary
        print("\n" + "=" * 50)
        print("🏁 TEST SUMMARY")
        print("=" * 50)
        
        print(f"✅ Passed: {len(passed_tests)}")
        for test in passed_tests:
            print(f"   • {test}")
        
        print(f"\n❌ Failed: {len(failed_tests)}")
        for test in failed_tests:
            print(f"   • {test}")
        
        if failed_tests:
            print(f"\n⚠️  {len(failed_tests)} tests failed")
            return False
        else:
            print(f"\n🎉 All {len(passed_tests)} tests passed!")
            return True
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_comprehensive_suite()
        if success:
            print("\n✅ Comprehensive test suite is working correctly!")
        else:
            print("\n❌ Comprehensive test suite has issues.")
    except Exception as e:
        print(f"\n💥 Critical error during testing: {e}")
        import traceback
        traceback.print_exc()
