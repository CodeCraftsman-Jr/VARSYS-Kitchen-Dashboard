#!/usr/bin/env python3
"""
Quick demonstration of the enhanced notification system
Shows that category tests are working properly
"""

import sys
import os
from datetime import datetime
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.enhanced_notification_system import (
    get_notification_manager, NotificationPanel,
    notify_emergency, notify_security, notify_critical, notify_error,
    notify_maintenance, notify_inventory, notify_staff, notify_schedule,
    notify_budget, notify_recipe, notify_success, notify_info
)

def demo_category_notifications():
    """Demonstrate all category notifications"""
    print("🔔 Enhanced Notification System Demo")
    print("=" * 50)
    
    # Get the notification manager
    manager = get_notification_manager()
    
    print("📤 Sending test notifications for each category...")
    
    # Test each category with a short delay
    categories = [
        (notify_emergency, "🚨 Emergency", "Emergency notification test"),
        (notify_security, "🔒 Security", "Security alert test"),
        (notify_critical, "⚠️ Critical", "Critical system alert test"),
        (notify_error, "❌ Error", "Error notification test"),
        (notify_maintenance, "🔧 Maintenance", "Maintenance reminder test"),
        (notify_inventory, "📦 Inventory", "Inventory level test"),
        (notify_staff, "👥 Staff", "Staff notification test"),
        (notify_schedule, "📅 Schedule", "Schedule update test"),
        (notify_budget, "💰 Budget", "Budget alert test"),
        (notify_recipe, "🍳 Recipe", "Recipe update test"),
        (notify_success, "✅ Success", "Success notification test"),
        (notify_info, "ℹ️ Info", "Information notification test")
    ]
    
    for i, (func, title, message) in enumerate(categories, 1):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"  {i:2d}. Sending {title} at {timestamp}")
        
        func(
            f"{title} [{timestamp}]",
            f"{message} - Sent at {timestamp}",
            "Demo Script",
            True,  # show_toast
            True   # show_bell
        )
        
        time.sleep(0.5)  # Small delay between notifications
    
    print("\n✅ All category notifications sent!")
    
    # Get all notifications to verify they were created
    notifications = manager.get_notifications()
    print(f"📊 Total notifications in system: {len(notifications)}")
    
    # Show breakdown by category
    categories_count = {}
    for notification in notifications:
        cat = notification.get('category', 'unknown')
        categories_count[cat] = categories_count.get(cat, 0) + 1
    
    print("\n📂 Notifications by category:")
    for category, count in sorted(categories_count.items()):
        print(f"  • {category}: {count}")
    
    print("\n🎯 Creating notification panel to display results...")
    
    # Create and show the notification panel
    try:
        from PySide6.QtWidgets import QApplication
        
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create notification panel
        panel = NotificationPanel(notifications)
        panel.show()
        
        print("📱 Notification panel created and displayed!")
        print("   - Panel size: 450x550 pixels (improved spacing)")
        print("   - Enhanced margins and padding")
        print("   - Category filtering available")
        print("   - Priority-based visual indicators")
        
        print("\n🎮 Instructions:")
        print("   1. The notification panel should now be visible")
        print("   2. Try clicking the filter buttons (All, Critical, Errors, etc.)")
        print("   3. Notice the improved spacing and readability")
        print("   4. Click on notifications to mark them as read")
        print("   5. Close this terminal when done testing")
        
        # Keep the application running
        if not app.exec():
            return 0
            
    except ImportError:
        print("⚠️  GUI not available, but notifications were created successfully!")
        print("   Run the test_notification_system.py for full GUI testing")
    
    return 0

if __name__ == "__main__":
    sys.exit(demo_category_notifications())
