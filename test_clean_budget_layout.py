#!/usr/bin/env python3
"""
Test script to verify the cleaned up budget layout (old layout removed, new layout kept)
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_old_layout_removed():
    """Test that old layout elements are removed"""
    print("🧪 Testing old layout elements removal...")
    
    try:
        budget_manager_file = 'modules/budget_manager.py'
        if os.path.exists(budget_manager_file):
            with open(budget_manager_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that old layout elements are removed
            old_elements = [
                "populate_main_categories_table",
                "add_main_budget_category",
                "main_categories_table",
                "new_main_category_name",
                "new_main_category_budget",
                "add_main_category_btn",
                "main_categories_resizer"
            ]
            
            found_old_elements = []
            for element in old_elements:
                if element in content:
                    found_old_elements.append(element)
            
            if len(found_old_elements) == 0:
                print("✅ All old layout elements successfully removed")
                return True
            else:
                print(f"❌ Found old layout elements still present: {found_old_elements}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Old layout removal test failed: {e}")
        return False

def test_new_layout_preserved():
    """Test that new layout elements are preserved"""
    print("🧪 Testing new layout elements preservation...")
    
    try:
        budget_manager_file = 'modules/budget_manager.py'
        if os.path.exists(budget_manager_file):
            with open(budget_manager_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that new layout elements are preserved
            new_elements = [
                "Budget Category Hierarchy",
                "3-Level Budget Category Structure",
                "hierarchy_table",
                "populate_budget_hierarchy",
                "budget_category_combo",
                "budget_amount_spin",
                "update_budget_allocation"
            ]
            
            found_new_elements = []
            for element in new_elements:
                if element in content:
                    found_new_elements.append(element)
            
            if len(found_new_elements) >= 6:
                print(f"✅ New layout elements preserved: {len(found_new_elements)}/{len(new_elements)} found")
                return True
            else:
                print(f"❌ New layout elements incomplete: {len(found_new_elements)}/{len(new_elements)} found")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ New layout preservation test failed: {e}")
        return False

def test_method_calls_updated():
    """Test that method calls are updated to use new methods"""
    print("🧪 Testing method calls updated...")
    
    try:
        budget_manager_file = 'modules/budget_manager.py'
        if os.path.exists(budget_manager_file):
            with open(budget_manager_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that calls are updated to new methods
            if "populate_budget_hierarchy()" in content:
                print("✅ Method calls updated to use populate_budget_hierarchy")
                return True
            else:
                print("❌ Method calls not properly updated")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Method calls test failed: {e}")
        return False

def test_budget_structure_intact():
    """Test that budget structure is still intact"""
    print("🧪 Testing budget structure integrity...")
    
    try:
        budget_categories_file = 'data/budget_categories.csv'
        if os.path.exists(budget_categories_file):
            with open(budget_categories_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for the 3 main categories
            main_categories = ["Kitchen Essentials", "Maintenance", "Gas"]
            found_categories = []
            
            for category in main_categories:
                if category in content:
                    found_categories.append(category)
            
            if len(found_categories) == 3:
                print("✅ Budget structure intact: All 3 main categories present")
                return True
            else:
                print(f"❌ Budget structure damaged: Only {len(found_categories)}/3 main categories found")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Budget structure test failed: {e}")
        return False

def main():
    """Run all cleanup verification tests"""
    print("🚀 Starting budget layout cleanup verification...")
    print("=" * 70)
    
    tests = [
        test_old_layout_removed,
        test_new_layout_preserved,
        test_method_calls_updated,
        test_budget_structure_intact
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Budget layout cleanup successful!")
        print()
        print("✅ Cleanup Results:")
        print("  1. ✅ Old layout elements removed")
        print("  2. ✅ New 3-level hierarchy layout preserved")
        print("  3. ✅ Method calls updated to new implementation")
        print("  4. ✅ Budget structure integrity maintained")
        print()
        print("💡 Current Implementation:")
        print("  • Only new 3-level hierarchy display")
        print("  • Budget allocation at main category level")
        print("  • Clean, simplified interface")
        print("  • No conflicting old layout elements")
        return True
    else:
        print("⚠️ Some cleanup issues detected.")
        print(f"   {passed} out of {total} checks passed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
