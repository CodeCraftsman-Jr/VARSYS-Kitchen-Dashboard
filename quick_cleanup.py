#!/usr/bin/env python3
"""
Quick Sample Data Cleanup
Removes sample data generated during testing
"""

import os
import shutil
from datetime import datetime

def quick_cleanup():
    """Quick cleanup of sample data"""
    print("🧹 Quick Sample Data Cleanup")
    print("=" * 40)
    
    removed_count = 0
    
    # Remove test data directory
    tests_data_dir = os.path.join('tests', 'data')
    if os.path.exists(tests_data_dir):
        try:
            shutil.rmtree(tests_data_dir)
            print(f"✅ Removed test data directory: {tests_data_dir}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove test data directory: {e}")
    
    # Remove test report files
    for file in os.listdir('.'):
        if file.startswith('test_report_') and file.endswith('.txt'):
            try:
                os.remove(file)
                print(f"✅ Removed test report: {file}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    # Remove sample data files from main data directory (optional)
    data_dir = 'data'
    sample_files = [
        'inventory.csv', 'shopping_list.csv', 'recipes.csv', 'recipe_ingredients.csv',
        'meal_plan.csv', 'sales.csv', 'budget.csv', 'waste.csv', 'cleaning_maintenance.csv',
        'items.csv', 'categories.csv', 'pricing.csv', 'packing_materials.csv',
        'recipe_packing_materials.csv', 'sales_orders.csv'
    ]
    
    print("\nDo you want to remove sample data from main data directory? (y/N): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        if os.path.exists(data_dir):
            for filename in sample_files:
                file_path = os.path.join(data_dir, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"✅ Removed: {filename}")
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Failed to remove {filename}: {e}")
    
    print(f"\n📊 Cleanup Summary: {removed_count} items removed")
    print("✅ Quick cleanup completed!")

if __name__ == "__main__":
    quick_cleanup()
