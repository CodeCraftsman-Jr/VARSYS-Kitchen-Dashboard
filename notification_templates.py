#!/usr/bin/env python3
"""
Notification Templates System
Provides pre-built templates for common notification scenarios
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.enhanced_notification_system import (
    get_notification_manager,
    notify_emergency, notify_critical, notify_error, notify_warning,
    notify_success, notify_info, notify_inventory, notify_staff,
    notify_schedule, notify_budget, notify_recipe, notify_maintenance
)

class TemplateType(Enum):
    """Types of notification templates"""
    SYSTEM_STATUS = "system_status"
    INVENTORY_ALERT = "inventory_alert"
    STAFF_NOTIFICATION = "staff_notification"
    FINANCIAL_ALERT = "financial_alert"
    MAINTENANCE_REMINDER = "maintenance_reminder"
    RECIPE_UPDATE = "recipe_update"
    SCHEDULE_CHANGE = "schedule_change"
    SECURITY_ALERT = "security_alert"
    PERFORMANCE_REPORT = "performance_report"
    BACKUP_STATUS = "backup_status"

@dataclass
class NotificationTemplate:
    """Template for generating consistent notifications"""
    template_id: str
    template_type: TemplateType
    title_template: str
    message_template: str
    category: str
    priority: int
    default_source: str
    icon: str
    color: str
    requires_action: bool = False
    auto_dismiss: bool = False
    escalation_minutes: int = 0

class NotificationTemplateManager:
    """Manages notification templates and generates notifications from them"""
    
    def __init__(self):
        self.notification_manager = get_notification_manager()
        self.templates: Dict[str, NotificationTemplate] = {}
        self.setup_default_templates()
    
    def setup_default_templates(self):
        """Setup comprehensive default templates"""
        
        # System Status Templates
        self.add_template(NotificationTemplate(
            template_id="system_startup",
            template_type=TemplateType.SYSTEM_STATUS,
            title_template="🚀 System Ready",
            message_template="{system_name} has started successfully. All modules loaded and operational.",
            category="system",
            priority=16,
            default_source="System",
            icon="🚀",
            color="#10b981",
            auto_dismiss=True
        ))
        
        self.add_template(NotificationTemplate(
            template_id="system_shutdown",
            template_type=TemplateType.SYSTEM_STATUS,
            title_template="🔄 System Shutdown",
            message_template="{system_name} is shutting down. All data has been saved.",
            category="system",
            priority=12,
            default_source="System",
            icon="🔄",
            color="#f59e0b"
        ))
        
        self.add_template(NotificationTemplate(
            template_id="system_error",
            template_type=TemplateType.SYSTEM_STATUS,
            title_template="❌ System Error",
            message_template="Critical error in {module_name}: {error_message}",
            category="error",
            priority=2,
            default_source="System",
            icon="❌",
            color="#ef4444",
            requires_action=True,
            escalation_minutes=15
        ))
        
        # Inventory Alert Templates
        self.add_template(NotificationTemplate(
            template_id="low_stock",
            template_type=TemplateType.INVENTORY_ALERT,
            title_template="📦 Low Stock Alert",
            message_template="{item_name} is running low. Current stock: {current_quantity} {unit}. Minimum required: {minimum_quantity} {unit}.",
            category="inventory",
            priority=7,
            default_source="Inventory System",
            icon="📦",
            color="#f59e0b",
            requires_action=True
        ))
        
        self.add_template(NotificationTemplate(
            template_id="out_of_stock",
            template_type=TemplateType.INVENTORY_ALERT,
            title_template="🚨 Out of Stock",
            message_template="{item_name} is completely out of stock! Immediate restocking required.",
            category="critical",
            priority=3,
            default_source="Inventory System",
            icon="🚨",
            color="#ef4444",
            requires_action=True,
            escalation_minutes=30
        ))
        
        self.add_template(NotificationTemplate(
            template_id="expiry_warning",
            template_type=TemplateType.INVENTORY_ALERT,
            title_template="⏰ Expiry Warning",
            message_template="{item_name} expires in {days_until_expiry} days (Expiry: {expiry_date}). Consider using soon.",
            category="warning",
            priority=8,
            default_source="Inventory System",
            icon="⏰",
            color="#f59e0b"
        ))
        
        # Staff Notification Templates
        self.add_template(NotificationTemplate(
            template_id="shift_reminder",
            template_type=TemplateType.STAFF_NOTIFICATION,
            title_template="👥 Shift Reminder",
            message_template="{staff_name}, your shift starts in {minutes_until_shift} minutes. Location: {location}.",
            category="staff",
            priority=9,
            default_source="Staff Management",
            icon="👥",
            color="#3b82f6"
        ))
        
        self.add_template(NotificationTemplate(
            template_id="overtime_alert",
            template_type=TemplateType.STAFF_NOTIFICATION,
            title_template="⏰ Overtime Alert",
            message_template="{staff_name} has worked {hours_worked} hours today. Overtime threshold reached.",
            category="staff",
            priority=6,
            default_source="Staff Management",
            icon="⏰",
            color="#f59e0b",
            requires_action=True
        ))
        
        # Financial Alert Templates
        self.add_template(NotificationTemplate(
            template_id="budget_exceeded",
            template_type=TemplateType.FINANCIAL_ALERT,
            title_template="💰 Budget Exceeded",
            message_template="{category_name} budget exceeded! Spent: {amount_spent}, Budget: {budget_limit}. Overage: {overage_amount}.",
            category="budget",
            priority=5,
            default_source="Budget System",
            icon="💰",
            color="#ef4444",
            requires_action=True
        ))
        
        self.add_template(NotificationTemplate(
            template_id="large_expense",
            template_type=TemplateType.FINANCIAL_ALERT,
            title_template="💳 Large Expense Alert",
            message_template="Large expense recorded: {expense_amount} for {expense_description}. Requires approval.",
            category="budget",
            priority=6,
            default_source="Expense System",
            icon="💳",
            color="#f59e0b",
            requires_action=True
        ))
        
        # Maintenance Templates
        self.add_template(NotificationTemplate(
            template_id="maintenance_due",
            template_type=TemplateType.MAINTENANCE_REMINDER,
            title_template="🔧 Maintenance Due",
            message_template="{equipment_name} is due for maintenance. Last service: {last_service_date}. Schedule service soon.",
            category="maintenance",
            priority=8,
            default_source="Maintenance System",
            icon="🔧",
            color="#f59e0b",
            requires_action=True
        ))
        
        self.add_template(NotificationTemplate(
            template_id="equipment_failure",
            template_type=TemplateType.MAINTENANCE_REMINDER,
            title_template="⚠️ Equipment Failure",
            message_template="{equipment_name} has failed and requires immediate attention. Error: {error_code}.",
            category="critical",
            priority=2,
            default_source="Equipment Monitor",
            icon="⚠️",
            color="#ef4444",
            requires_action=True,
            escalation_minutes=10
        ))
        
        # Recipe Templates
        self.add_template(NotificationTemplate(
            template_id="recipe_updated",
            template_type=TemplateType.RECIPE_UPDATE,
            title_template="🍳 Recipe Updated",
            message_template="Recipe '{recipe_name}' has been updated. Changes: {change_summary}.",
            category="recipe",
            priority=10,
            default_source="Recipe System",
            icon="🍳",
            color="#10b981",
            auto_dismiss=True
        ))
        
        # Schedule Templates
        self.add_template(NotificationTemplate(
            template_id="schedule_change",
            template_type=TemplateType.SCHEDULE_CHANGE,
            title_template="📅 Schedule Change",
            message_template="Schedule updated for {date}. {change_description}. Please review your assignments.",
            category="schedule",
            priority=7,
            default_source="Schedule System",
            icon="📅",
            color="#3b82f6",
            requires_action=True
        ))
        
        # Security Templates
        self.add_template(NotificationTemplate(
            template_id="security_breach",
            template_type=TemplateType.SECURITY_ALERT,
            title_template="🔒 Security Alert",
            message_template="Potential security breach detected: {breach_description}. Immediate action required.",
            category="security",
            priority=1,
            default_source="Security System",
            icon="🔒",
            color="#ef4444",
            requires_action=True,
            escalation_minutes=5
        ))
        
        # Performance Templates
        self.add_template(NotificationTemplate(
            template_id="daily_summary",
            template_type=TemplateType.PERFORMANCE_REPORT,
            title_template="📊 Daily Summary",
            message_template="Daily performance summary: {sales_count} orders, {revenue_amount} revenue, {efficiency_percent}% efficiency.",
            category="info",
            priority=12,
            default_source="Analytics",
            icon="📊",
            color="#10b981",
            auto_dismiss=True
        ))
    
    def add_template(self, template: NotificationTemplate):
        """Add a template to the manager"""
        self.templates[template.template_id] = template
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, template_type: TemplateType = None) -> List[NotificationTemplate]:
        """List all templates, optionally filtered by type"""
        if template_type:
            return [t for t in self.templates.values() if t.template_type == template_type]
        return list(self.templates.values())
    
    def send_from_template(self, template_id: str, **kwargs) -> bool:
        """Send a notification using a template"""
        template = self.get_template(template_id)
        if not template:
            print(f"❌ Template '{template_id}' not found")
            return False
        
        try:
            # Format title and message with provided kwargs
            title = template.title_template.format(**kwargs)
            message = template.message_template.format(**kwargs)
            
            # Get source from kwargs or use default
            source = kwargs.get('source', template.default_source)
            
            # Send notification using appropriate function
            if template.category == "emergency":
                return notify_emergency(title, message, source, True, True)
            elif template.category == "critical":
                return notify_critical(title, message, source, True, True)
            elif template.category == "error":
                return notify_error(title, message, source, True, True)
            elif template.category == "warning":
                return notify_warning(title, message, source, True, True)
            elif template.category == "success":
                return notify_success(title, message, source, True, True)
            elif template.category == "inventory":
                return notify_inventory(title, message, source, True, True)
            elif template.category == "staff":
                return notify_staff(title, message, source, True, True)
            elif template.category == "schedule":
                return notify_schedule(title, message, source, True, True)
            elif template.category == "budget":
                return notify_budget(title, message, source, True, True)
            elif template.category == "recipe":
                return notify_recipe(title, message, source, True, True)
            elif template.category == "maintenance":
                return notify_maintenance(title, message, source, True, True)
            else:
                return notify_info(title, message, source, True, True)
                
        except KeyError as e:
            print(f"❌ Missing required parameter for template '{template_id}': {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending notification from template '{template_id}': {e}")
            return False

# Convenience functions for common scenarios
def notify_low_stock(item_name: str, current_quantity: int, minimum_quantity: int, unit: str = "units"):
    """Send a low stock notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template(
        "low_stock",
        item_name=item_name,
        current_quantity=current_quantity,
        minimum_quantity=minimum_quantity,
        unit=unit
    )

def notify_out_of_stock(item_name: str):
    """Send an out of stock notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template("out_of_stock", item_name=item_name)

def notify_expiry_warning(item_name: str, days_until_expiry: int, expiry_date: str):
    """Send an expiry warning notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template(
        "expiry_warning",
        item_name=item_name,
        days_until_expiry=days_until_expiry,
        expiry_date=expiry_date
    )

def notify_shift_reminder(staff_name: str, minutes_until_shift: int, location: str = "Kitchen"):
    """Send a shift reminder notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template(
        "shift_reminder",
        staff_name=staff_name,
        minutes_until_shift=minutes_until_shift,
        location=location
    )

def notify_budget_exceeded(category_name: str, amount_spent: float, budget_limit: float, currency: str = "₹"):
    """Send a budget exceeded notification"""
    manager = NotificationTemplateManager()
    overage = amount_spent - budget_limit
    return manager.send_from_template(
        "budget_exceeded",
        category_name=category_name,
        amount_spent=f"{currency}{amount_spent:,.2f}",
        budget_limit=f"{currency}{budget_limit:,.2f}",
        overage_amount=f"{currency}{overage:,.2f}"
    )

def notify_maintenance_due(equipment_name: str, last_service_date: str):
    """Send a maintenance due notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template(
        "maintenance_due",
        equipment_name=equipment_name,
        last_service_date=last_service_date
    )

def notify_system_startup(system_name: str = "VARSYS Kitchen Dashboard"):
    """Send a system startup notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template("system_startup", system_name=system_name)

def notify_daily_summary(sales_count: int, revenue_amount: float, efficiency_percent: int, currency: str = "₹"):
    """Send a daily summary notification"""
    manager = NotificationTemplateManager()
    return manager.send_from_template(
        "daily_summary",
        sales_count=sales_count,
        revenue_amount=f"{currency}{revenue_amount:,.2f}",
        efficiency_percent=efficiency_percent
    )

def demo_notification_templates():
    """Demonstrate the notification templates system"""
    print("🎯 Notification Templates System Demo")
    print("=" * 50)
    
    manager = NotificationTemplateManager()
    
    print(f"📋 Available Templates: {len(manager.templates)}")
    
    # Group templates by type
    by_type = {}
    for template in manager.templates.values():
        template_type = template.template_type.value
        if template_type not in by_type:
            by_type[template_type] = []
        by_type[template_type].append(template)
    
    for template_type, templates in by_type.items():
        print(f"\n📂 {template_type.replace('_', ' ').title()}:")
        for template in templates:
            print(f"   • {template.template_id}: {template.title_template}")
    
    print("\n🧪 Testing Template Notifications:")
    
    # Test various templates
    test_cases = [
        ("Low Stock", lambda: notify_low_stock("Tomatoes", 5, 20, "kg")),
        ("Shift Reminder", lambda: notify_shift_reminder("John Doe", 30, "Main Kitchen")),
        ("Budget Alert", lambda: notify_budget_exceeded("Vegetables", 15000, 12000)),
        ("Maintenance Due", lambda: notify_maintenance_due("Oven #1", "2025-05-15")),
        ("Daily Summary", lambda: notify_daily_summary(45, 25000, 92)),
        ("System Startup", lambda: notify_system_startup())
    ]
    
    for test_name, test_func in test_cases:
        try:
            result = test_func()
            status = "✅ Sent" if result else "❌ Failed"
            print(f"   {status}: {test_name}")
        except Exception as e:
            print(f"   ❌ Error in {test_name}: {e}")
    
    print("\n✅ Template demonstration completed!")
    return manager

if __name__ == "__main__":
    demo_notification_templates()
