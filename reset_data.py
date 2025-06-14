#!/usr/bin/env python3
"""
Data Reset Utility
Resets application data to clean state
"""

import os
import shutil
import csv
from datetime import datetime

def create_backup():
    """Create backup of current data"""
    if not os.path.exists('data'):
        print("❌ No data directory found to backup")
        return False
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data_backup_{timestamp}"
    
    try:
        print(f"📦 Creating backup at: {backup_path}")
        shutil.copytree('data', backup_path)
        print(f"✅ Backup created successfully!")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def reset_to_empty_csv():
    """Reset CSV files to empty state with headers only"""
    print("\n🔄 Resetting CSV files to empty state...")
    print("-" * 40)
    
    # Define empty CSV files with headers
    empty_files = {
        'inventory.csv': 'item_id,item_name,category,quantity,unit,price_per_unit,location,expiry_date,reorder_level',
        'recipes.csv': 'recipe_id,recipe_name,category,servings,prep_time,cook_time,description',
        'recipe_ingredients.csv': 'recipe_id,item_id,quantity,unit',
        'sales.csv': 'sale_id,item_name,quantity,price_per_unit,total_amount,customer,date',
        'sales_orders.csv': 'order_id,customer_name,items,total_amount,order_date,status',
        'shopping_list.csv': 'item_id,item_name,category,quantity,unit,priority,status',
        'categories.csv': 'category_id,category_name,description',
        'items.csv': 'item_id,item_name,category,unit,description',
        'meal_plan.csv': 'plan_id,recipe_id,date,meal_type,servings',
        'meal_plan_items.csv': 'plan_id,recipe_id,date,meal_type,servings',
        'budget.csv': 'category,budgeted_amount,actual_amount,month,year',
        'waste.csv': 'waste_id,item_name,quantity,unit,reason,date,cost',
        'cleaning_maintenance.csv': 'task_id,task_name,frequency,last_completed,next_due,status',
        'pricing.csv': 'recipe_id,ingredient_cost,making_cost,packaging_cost,total_cost,selling_price,profit_margin',
        'packing_materials.csv': 'material_id,material_name,quantity,unit,cost_per_unit,supplier',
        'recipe_packing_materials.csv': 'recipe_id,material_id,quantity,unit',
        'gas_usage.csv': 'date,usage_amount,cost,recipe_id',
        'electricity_usage.csv': 'date,usage_amount,cost,recipe_id',
        'gas_orders.csv': 'order_id,supplier,quantity,cost,order_date,delivery_date',
        'gas_tracking.csv': 'date,opening_stock,usage,closing_stock,cost_per_unit',
        'expenses.csv': 'expense_id,category,amount,description,date',
        'packing_materials_purchase_history.csv': 'purchase_id,material_id,quantity,cost,supplier,date',
        'packing_materials_usage_history.csv': 'usage_id,material_id,quantity,recipe_id,date'
    }
    
    os.makedirs('data', exist_ok=True)
    
    reset_count = 0
    for filename, header in empty_files.items():
        file_path = os.path.join('data', filename)
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write(header + '\n')
            print(f"✅ Reset: {filename}")
            reset_count += 1
        except Exception as e:
            print(f"❌ Failed to reset {filename}: {e}")
    
    # Reset JSON files
    json_files = {
        'notifications.json': '[]',
        'missing_ingredients.json': '[]',
        'activities.json': '[]',
        'gas_cost_config.json': '{"cost_per_unit": 50.0, "last_updated": "2024-01-01"}',
        'inventory_column_settings.json': '{"visible_columns": ["item_name", "category", "quantity", "unit", "price_per_unit", "location"]}'
    }
    
    for filename, content in json_files.items():
        file_path = os.path.join('data', filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Reset: {filename}")
            reset_count += 1
        except Exception as e:
            print(f"❌ Failed to reset {filename}: {e}")
    
    # Remove daily activities directory
    daily_activities_dir = os.path.join('data', 'daily_activities')
    if os.path.exists(daily_activities_dir):
        try:
            shutil.rmtree(daily_activities_dir)
            print(f"✅ Removed: daily_activities/")
            reset_count += 1
        except Exception as e:
            print(f"❌ Failed to remove daily_activities: {e}")
    
    print(f"\n📊 Reset Summary: {reset_count} files reset to empty state")
    return reset_count

def main():
    """Main function"""
    print("🔄 Kitchen Dashboard - Data Reset Utility")
    print("=" * 50)
    print()
    print("This utility will reset your application data.")
    print("⚠️  WARNING: This will remove all your current data!")
    print()
    
    # Ask for confirmation
    confirm = input("Do you want to continue? (type 'YES' to confirm): ").strip()
    
    if confirm != 'YES':
        print("❌ Reset cancelled")
        return
    
    # Ask about backup
    backup_choice = input("\nCreate backup before reset? (Y/n): ").strip().lower()
    
    if backup_choice != 'n':
        if not create_backup():
            continue_choice = input("Backup failed. Continue anyway? (y/N): ").strip().lower()
            if continue_choice != 'y':
                print("❌ Reset cancelled")
                return
    
    # Perform reset
    reset_count = reset_to_empty_csv()
    
    if reset_count > 0:
        print("\n✅ Data reset completed successfully!")
        print("📝 Your application now has clean, empty data files.")
        print("🚀 You can start fresh with your Kitchen Dashboard!")
    else:
        print("\n❌ Data reset failed")

if __name__ == "__main__":
    main()
