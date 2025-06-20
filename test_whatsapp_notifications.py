"""
Test script for WhatsApp Automated Notifications
This script tests all notification types to ensure they work correctly
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import time

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_test_data():
    """Create test data for notifications"""
    print("📋 Creating test data...")
    
    # Create test inventory data with low stock items
    inventory_data = {
        'item_id': [1, 2, 3, 4, 5],
        'item_name': ['Test Oil', 'Test Rice', 'Test Vegetables', 'Test Spices', 'Test Salt'],
        'category': ['Oils', 'Grains', 'Vegetables', 'Spices', 'Seasonings'],
        'quantity': [2, 5, 1, 8, 0],  # Some items below reorder level
        'unit': ['liters', 'kg', 'kg', 'kg', 'kg'],
        'reorder_level': [10, 20, 5, 10, 3],  # Reorder levels
        'qty_purchased': [50, 100, 20, 30, 10],
        'qty_used': [48, 95, 19, 22, 10],  # Used quantities
        'price_per_unit': [150, 80, 60, 200, 25]
    }
    
    # Create test cleaning tasks due today
    cleaning_data = {
        'task_name': ['Clean Kitchen Floor', 'Sanitize Counters', 'Clean Equipment'],
        'assigned_to': ['Kitchen Staff', 'Chef', 'Assistant'],
        'location': ['Main Kitchen', 'Prep Area', 'Storage'],
        'next_due': [
            datetime.now().date(),
            datetime.now().date(),
            (datetime.now() - timedelta(days=1)).date()  # Overdue task
        ]
    }
    
    # Create test packing materials with low stock
    packing_data = {
        'material_name': ['Food Containers', 'Plastic Bags', 'Labels', 'Tape'],
        'current_stock': [5, 0, 15, 8],  # Some low/out of stock
        'minimum_stock': [20, 10, 50, 15],
        'unit': ['pieces', 'pieces', 'pieces', 'rolls']
    }
    
    # Create test gas tracking data
    gas_data = {
        'cylinder_id': ['CYL-001'],
        'status': ['Active'],
        'estimated_days_remaining': [1],  # Critical level
        'last_updated': [datetime.now()]
    }
    
    return {
        'inventory': pd.DataFrame(inventory_data),
        'cleaning_maintenance': pd.DataFrame(cleaning_data),
        'packing_materials': pd.DataFrame(packing_data),
        'gas_tracking': pd.DataFrame(gas_data)
    }

def test_notification_system():
    """Test the WhatsApp notification system"""
    print("🧪 Starting WhatsApp Notifications Test")
    print("=" * 50)
    
    try:
        # Import the notification system
        from modules.whatsapp_automated_notifications import WhatsAppAutomatedNotifications
        
        # Create test data
        test_data = create_test_data()
        
        # Initialize notification system
        print("🔧 Initializing notification system...")
        notifications = WhatsAppAutomatedNotifications(data=test_data)
        
        # Test 1: Low Stock Notifications
        print("\n📦 Testing Low Stock Notifications...")
        notifications.check_low_stock_notifications()
        print("✅ Low stock check completed")
        
        # Test 2: Cleaning Task Reminders
        print("\n🧹 Testing Cleaning Task Reminders...")
        notifications.check_cleaning_reminders()
        print("✅ Cleaning reminders check completed")
        
        # Test 3: Packing Materials Alerts
        print("\n📦 Testing Packing Materials Alerts...")
        notifications.check_packing_materials_alerts()
        print("✅ Packing materials check completed")
        
        # Test 4: Gas Level Warnings
        print("\n⛽ Testing Gas Level Warnings...")
        notifications.check_gas_level_warnings()
        print("✅ Gas level check completed")
        
        # Test 5: General Test Notification
        print("\n📧 Testing General Notification...")
        success = notifications.send_test_notification()
        if success:
            print("✅ Test notification sent successfully")
        else:
            print("⚠️ Test notification failed (WhatsApp may not be connected)")
        
        # Display test results
        print("\n📊 Test Results Summary:")
        print("=" * 30)
        
        # Check which items would trigger notifications
        inventory_df = test_data['inventory']
        low_stock_items = []
        for _, item in inventory_df.iterrows():
            current_qty = item['qty_purchased'] - item['qty_used']
            if current_qty <= item['reorder_level']:
                low_stock_items.append(f"- {item['item_name']}: {current_qty} {item['unit']} (reorder at {item['reorder_level']})")
        
        if low_stock_items:
            print(f"📦 Low Stock Items ({len(low_stock_items)}):")
            for item in low_stock_items:
                print(f"  {item}")
        
        # Check cleaning tasks
        cleaning_df = test_data['cleaning_maintenance']
        due_tasks = []
        today = datetime.now().date()
        for _, task in cleaning_df.iterrows():
            due_date = pd.to_datetime(task['next_due']).date()
            if due_date <= today:
                due_tasks.append(f"- {task['task_name']} (assigned to {task['assigned_to']})")
        
        if due_tasks:
            print(f"\n🧹 Due Cleaning Tasks ({len(due_tasks)}):")
            for task in due_tasks:
                print(f"  {task}")
        
        # Check packing materials
        packing_df = test_data['packing_materials']
        low_packing = []
        for _, material in packing_df.iterrows():
            if material['current_stock'] <= material['minimum_stock']:
                status = "OUT OF STOCK" if material['current_stock'] == 0 else "LOW STOCK"
                low_packing.append(f"- {material['material_name']}: {material['current_stock']} {material['unit']} ({status})")
        
        if low_packing:
            print(f"\n📦 Packing Materials Issues ({len(low_packing)}):")
            for material in low_packing:
                print(f"  {material}")
        
        # Check gas levels
        gas_df = test_data['gas_tracking']
        for _, cylinder in gas_df.iterrows():
            days_remaining = cylinder['estimated_days_remaining']
            if days_remaining <= 3:
                severity = "CRITICAL" if days_remaining <= 1 else "WARNING"
                print(f"\n⛽ Gas Level {severity}: {cylinder['cylinder_id']} - {days_remaining} days remaining")
        
        print(f"\n🎉 All notification tests completed successfully!")
        print(f"📱 If WhatsApp is connected, messages should have been sent to 'Abiram's Kitchen' group")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure the WhatsApp integration modules are available")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 WhatsApp Automated Notifications Test Suite")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the test
    success = test_notification_system()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
        print("📱 Check the 'Abiram's Kitchen' WhatsApp group for test messages")
    else:
        print("❌ Some tests failed. Check the error messages above.")
    
    print("\n💡 To use in production:")
    print("1. Ensure WhatsApp Web is connected")
    print("2. The automated notifications will run in the background")
    print("3. Real-time notifications will be sent when data changes")
    print("4. Use the test buttons in the WhatsApp settings to verify functionality")

if __name__ == "__main__":
    main()
