#!/usr/bin/env python3
"""
Test only the failing modules to identify specific issues
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

def test_failing_modules():
    """Test only the failing modules"""
    print("🧪 Testing Failing Modules")
    print("=" * 40)
    
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
    
    # Test only the failing modules
    failing_modules = [
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
            'name': 'Firebase Module',
            'module': 'modules.firebase_sync',
            'class': 'FirebaseSync',
            'args': (None,)  # parent argument
        }
    ]
    
    for module_info in failing_modules:
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
            
        except Exception as e:
            print(f"   ❌ {module_info['name']}: FAILED - {e}")
            
            # Print detailed error info
            import traceback
            print(f"   📋 Full error traceback:")
            traceback.print_exc()
            print()

if __name__ == "__main__":
    test_failing_modules()
