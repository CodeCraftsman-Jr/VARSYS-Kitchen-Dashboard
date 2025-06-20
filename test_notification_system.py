#!/usr/bin/env python3
"""
Enhanced Notification System Testing Interface
Demonstrates all notification categories, priorities, and improved spacing
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QLabel, QComboBox, QTextEdit,
                               QSpinBox, QCheckBox, QGroupBox, QScrollArea, QFrame,
                               QGridLayout, QTabWidget, QProgressBar, QSlider)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor

from modules.enhanced_notification_system import (
    get_notification_manager, NotificationPanel,
    notify_emergency, notify_security, notify_critical, notify_error, notify_failure,
    notify_maintenance, notify_resource, notify_inventory, notify_staff, notify_schedule,
    notify_budget, notify_recipe, notify_completion, notify_sync, notify_update,
    notify_startup, notify_debug, notify_warning, notify_success, notify_info, notify_system
)

class NotificationTestingInterface(QMainWindow):
    """Comprehensive notification testing interface"""
    
    def __init__(self):
        super().__init__()
        self.notification_manager = get_notification_manager()
        self.notification_panel = None
        self.auto_demo_timer = QTimer()
        self.auto_demo_timer.timeout.connect(self.send_random_notification)
        
        self.init_ui()
        self.setup_demo_data()
        
    def init_ui(self):
        """Initialize the testing interface"""
        self.setWindowTitle("Enhanced Notification System - Testing Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Notification display
        right_panel = self.create_display_panel()
        main_layout.addWidget(right_panel, 1)
        
    def create_control_panel(self):
        """Create the control panel with testing options"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔔 Notification System Tester")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Quick test buttons
        quick_test_group = self.create_quick_test_group()
        layout.addWidget(quick_test_group)
        
        # Category testing
        category_group = self.create_category_test_group()
        layout.addWidget(category_group)
        
        # Custom notification
        custom_group = self.create_custom_notification_group()
        layout.addWidget(custom_group)
        
        # Auto demo controls
        demo_group = self.create_demo_controls_group()
        layout.addWidget(demo_group)
        
        # Statistics
        stats_group = self.create_statistics_group()
        layout.addWidget(stats_group)

        # Status display
        status_group = self.create_status_group()
        layout.addWidget(status_group)

        layout.addStretch()
        
        scroll_area.setWidget(control_widget)
        return scroll_area
        
    def create_quick_test_group(self):
        """Create quick test buttons group"""
        group = QGroupBox("🚀 Quick Tests")
        layout = QVBoxLayout(group)
        
        # Test spacing button
        spacing_btn = QPushButton("Test Improved Spacing")
        spacing_btn.setStyleSheet("background-color: #e74c3c;")
        spacing_btn.clicked.connect(self.test_spacing_improvements)
        layout.addWidget(spacing_btn)
        
        # Test all categories
        categories_btn = QPushButton("Test All Categories")
        categories_btn.setStyleSheet("background-color: #f39c12;")
        categories_btn.clicked.connect(self.test_all_categories)
        layout.addWidget(categories_btn)
        
        # Test priority levels
        priority_btn = QPushButton("Test Priority Levels")
        priority_btn.setStyleSheet("background-color: #9b59b6;")
        priority_btn.clicked.connect(self.test_priority_levels)
        layout.addWidget(priority_btn)
        
        # Show notification panel
        panel_btn = QPushButton("Show Notification Panel")
        panel_btn.setStyleSheet("background-color: #27ae60;")
        panel_btn.clicked.connect(self.show_notification_panel)
        layout.addWidget(panel_btn)
        
        return group
        
    def create_category_test_group(self):
        """Create category testing group"""
        group = QGroupBox("📂 Category Tests")
        layout = QGridLayout(group)
        
        # Category buttons with colors
        categories = [
            ("🚨 Emergency", notify_emergency, "#c0392b"),
            ("🔒 Security", notify_security, "#8e44ad"),
            ("⚠️ Critical", notify_critical, "#e74c3c"),
            ("❌ Error", notify_error, "#e67e22"),
            ("🔧 Maintenance", notify_maintenance, "#f39c12"),
            ("📦 Inventory", notify_inventory, "#3498db"),
            ("👥 Staff", notify_staff, "#2ecc71"),
            ("📅 Schedule", notify_schedule, "#1abc9c"),
            ("💰 Budget", notify_budget, "#34495e"),
            ("🍳 Recipe", notify_recipe, "#e91e63"),
            ("✅ Success", notify_success, "#27ae60"),
            ("ℹ️ Info", notify_info, "#3498db")
        ]
        
        for i, (name, func, color) in enumerate(categories):
            btn = QPushButton(name)
            btn.setStyleSheet(f"background-color: {color};")
            btn.clicked.connect(lambda checked, f=func: self.send_category_notification(f))
            layout.addWidget(btn, i // 3, i % 3)
            
        return group
        
    def create_custom_notification_group(self):
        """Create custom notification controls"""
        group = QGroupBox("✏️ Custom Notification")
        layout = QVBoxLayout(group)
        
        # Title input
        self.title_input = QTextEdit()
        self.title_input.setPlaceholderText("Notification title...")
        self.title_input.setMaximumHeight(60)
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)
        
        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Notification message...")
        self.message_input.setMaximumHeight(80)
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.message_input)
        
        # Category and priority
        controls_layout = QHBoxLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "emergency", "security", "critical", "error", "failure",
            "maintenance", "resource", "inventory", "staff", "schedule",
            "budget", "recipe", "completion", "sync", "update",
            "startup", "debug", "warning", "success", "info", "system"
        ])
        controls_layout.addWidget(QLabel("Category:"))
        controls_layout.addWidget(self.category_combo)
        
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 20)
        self.priority_spin.setValue(10)
        controls_layout.addWidget(QLabel("Priority:"))
        controls_layout.addWidget(self.priority_spin)
        
        layout.addLayout(controls_layout)
        
        # Send button
        send_btn = QPushButton("Send Custom Notification")
        send_btn.clicked.connect(self.send_custom_notification)
        layout.addWidget(send_btn)
        
        return group
        
    def create_demo_controls_group(self):
        """Create auto demo controls"""
        group = QGroupBox("🎬 Auto Demo")
        layout = QVBoxLayout(group)
        
        # Demo controls
        demo_layout = QHBoxLayout()
        
        self.demo_btn = QPushButton("Start Demo")
        self.demo_btn.clicked.connect(self.toggle_auto_demo)
        demo_layout.addWidget(self.demo_btn)
        
        self.demo_interval = QSpinBox()
        self.demo_interval.setRange(1, 10)
        self.demo_interval.setValue(3)
        self.demo_interval.setSuffix(" sec")
        demo_layout.addWidget(QLabel("Interval:"))
        demo_layout.addWidget(self.demo_interval)
        
        layout.addLayout(demo_layout)
        
        # Clear all button
        clear_btn = QPushButton("Clear All Notifications")
        clear_btn.setStyleSheet("background-color: #e74c3c;")
        clear_btn.clicked.connect(self.clear_all_notifications)
        layout.addWidget(clear_btn)
        
        return group
        
    def create_statistics_group(self):
        """Create statistics display"""
        group = QGroupBox("📊 Statistics")
        layout = QVBoxLayout(group)
        
        self.stats_label = QLabel("No notifications yet")
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)
        
        # Update stats timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(1000)  # Update every second

        return group

    def create_display_panel(self):
        """Create the notification display panel"""
        group = QGroupBox("🔔 Live Notification Display")
        layout = QVBoxLayout(group)

        # Info label
        info_label = QLabel("Click 'Show Notification Panel' to see notifications with improved spacing!")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)

        # Demo preview area
        preview_area = QFrame()
        preview_area.setFrameStyle(QFrame.Box)
        preview_area.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                min-height: 400px;
            }
        """)

        preview_layout = QVBoxLayout(preview_area)
        preview_label = QLabel("📱 Notification Panel Preview\n\nUse the controls on the left to test notifications.\nThe actual notification panel will appear as a separate window.")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        preview_layout.addWidget(preview_label)

        layout.addWidget(preview_area)

        return group

    def create_status_group(self):
        """Create status display group"""
        group = QGroupBox("📱 Status")
        layout = QVBoxLayout(group)

        self.status_label = QLabel("Ready to test notifications")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)

        return group

    def setup_demo_data(self):
        """Setup demo notification data"""
        self.demo_notifications = [
            ("System Startup", "VARSYS Kitchen Dashboard initialized successfully", "system", 16),
            ("Low Stock Alert", "Tomatoes are running low (5 units remaining)", "inventory", 6),
            ("Staff Schedule", "John Doe shift starts in 30 minutes", "staff", 8),
            ("Recipe Updated", "Pasta Carbonara recipe has been modified", "recipe", 10),
            ("Budget Warning", "Monthly budget 85% utilized", "budget", 7),
            ("Maintenance Due", "Oven cleaning scheduled for tomorrow", "maintenance", 9),
            ("Order Complete", "Order #1234 has been successfully processed", "completion", 12),
            ("Security Alert", "Unauthorized access attempt detected", "security", 2),
            ("Critical Error", "Database connection failed", "critical", 1),
            ("Sync Complete", "Data synchronized with cloud successfully", "sync", 14)
        ]

    def test_spacing_improvements(self):
        """Test the improved spacing with various notification lengths"""
        notifications = [
            ("Short Title", "Brief message", "info", 10),
            ("Medium Length Notification Title", "This is a medium length message that should wrap properly with the improved spacing", "warning", 7),
            ("Very Long Notification Title That Should Wrap Properly", "This is a very long notification message that demonstrates the improved spacing and text wrapping capabilities. The enhanced margins and padding should make this much more readable than before.", "error", 4),
            ("📊 Rich Content", "✅ Success: All systems operational\n🔄 Status: Online\n📈 Performance: Excellent", "success", 11)
        ]

        for title, message, category, priority in notifications:
            self.notification_manager.notify(title, message, category, priority, "Spacing Test", True, True, 8000)

        # Show the panel to see the improvements
        self.show_notification_panel()

    def test_all_categories(self):
        """Test all notification categories"""
        category_tests = [
            (notify_emergency, "Emergency Test", "This is an emergency notification test"),
            (notify_security, "Security Test", "Security system notification test"),
            (notify_critical, "Critical Test", "Critical system alert test"),
            (notify_error, "Error Test", "Error notification test"),
            (notify_maintenance, "Maintenance Test", "Maintenance reminder test"),
            (notify_inventory, "Inventory Test", "Inventory level notification test"),
            (notify_staff, "Staff Test", "Staff schedule notification test"),
            (notify_budget, "Budget Test", "Budget alert notification test"),
            (notify_recipe, "Recipe Test", "Recipe update notification test"),
            (notify_success, "Success Test", "Success notification test")
        ]

        for func, title, message in category_tests:
            func(title, message, "Category Test", True, True)

        self.show_notification_panel()

    def test_priority_levels(self):
        """Test different priority levels"""
        priorities = [
            (1, "🚨 EMERGENCY", "Highest priority notification"),
            (3, "⚠️ CRITICAL", "Critical priority notification"),
            (7, "🟡 WARNING", "Warning priority notification"),
            (10, "ℹ️ INFO", "Information priority notification"),
            (15, "📝 DEBUG", "Debug priority notification"),
            (20, "💬 VERBOSE", "Lowest priority notification")
        ]

        for priority, title, message in priorities:
            self.notification_manager.notify(title, message, "info", priority, "Priority Test", True, True, 6000)

        self.show_notification_panel()

    def send_category_notification(self, notify_func):
        """Send a notification using the specified function"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        notify_func(
            f"Test Notification {timestamp}",
            f"This is a test notification sent at {timestamp} to demonstrate the category functionality.",
            "Test Interface",
            True, True
        )

        # Update status
        self.status_label.setText(f"✅ Sent {notify_func.__name__} notification at {timestamp}")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")

        # Show the notification panel and refresh it
        self.show_notification_panel()
        if self.notification_panel:
            notifications = self.notification_manager.get_notifications()
            self.notification_panel.refresh_notifications(notifications)

    def send_custom_notification(self):
        """Send a custom notification"""
        title = self.title_input.toPlainText().strip() or "Custom Notification"
        message = self.message_input.toPlainText().strip() or "Custom notification message"
        category = self.category_combo.currentText()
        priority = self.priority_spin.value()

        self.notification_manager.notify(title, message, category, priority, "Custom Test", True, True, 7000)

        # Update status
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"✅ Sent custom {category} notification at {timestamp}")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")

        # Show the notification panel and refresh it
        self.show_notification_panel()
        if self.notification_panel:
            notifications = self.notification_manager.get_notifications()
            self.notification_panel.refresh_notifications(notifications)

    def toggle_auto_demo(self):
        """Toggle auto demo mode"""
        if self.auto_demo_timer.isActive():
            self.auto_demo_timer.stop()
            self.demo_btn.setText("Start Demo")
            self.demo_btn.setStyleSheet("background-color: #27ae60;")
        else:
            interval = self.demo_interval.value() * 1000
            self.auto_demo_timer.start(interval)
            self.demo_btn.setText("Stop Demo")
            self.demo_btn.setStyleSheet("background-color: #e74c3c;")

    def send_random_notification(self):
        """Send a random demo notification"""
        title, message, category, priority = random.choice(self.demo_notifications)
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.notification_manager.notify(
            f"{title} [{timestamp}]",
            message,
            category,
            priority,
            "Auto Demo",
            True, True, 5000
        )

        # Refresh the notification panel if it's open
        if self.notification_panel and self.notification_panel.isVisible():
            notifications = self.notification_manager.get_notifications()
            self.notification_panel.refresh_notifications(notifications)

    def show_notification_panel(self):
        """Show the notification panel"""
        notifications = self.notification_manager.get_notifications()

        if self.notification_panel is None or not self.notification_panel.isVisible():
            self.notification_panel = NotificationPanel(notifications)
            self.notification_panel.show()

            # Position it next to the main window
            main_pos = self.pos()
            main_size = self.size()
            self.notification_panel.move(main_pos.x() + main_size.width() + 20, main_pos.y())
        else:
            # Panel is already open, just refresh it
            self.notification_panel.refresh_notifications(notifications)
            self.notification_panel.raise_()  # Bring to front

    def clear_all_notifications(self):
        """Clear all notifications"""
        self.notification_manager.clear_all()
        if self.notification_panel:
            self.notification_panel.refresh_notifications([])

    def update_statistics(self):
        """Update notification statistics"""
        notifications = self.notification_manager.get_notifications()
        total = len(notifications)
        unread = len([n for n in notifications if not n.get('read', False)])

        if total == 0:
            self.stats_label.setText("📊 No notifications yet")
            return

        # Count by category
        categories = {}
        priorities = {}

        for notification in notifications:
            cat = notification.get('category', 'unknown')
            pri = notification.get('priority', 10)

            categories[cat] = categories.get(cat, 0) + 1
            priorities[pri] = priorities.get(pri, 0) + 1

        # Format statistics
        stats_text = f"📊 Statistics:\n"
        stats_text += f"Total: {total} | Unread: {unread}\n\n"

        stats_text += "Categories:\n"
        for cat, count in sorted(categories.items()):
            stats_text += f"• {cat}: {count}\n"

        stats_text += f"\nPriority Distribution:\n"
        for pri, count in sorted(priorities.items()):
            stats_text += f"• P{pri}: {count}\n"

        self.stats_label.setText(stats_text)

def main():
    """Main function to run the notification testing interface"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Notification System Tester")
    app.setApplicationVersion("1.0")

    # Create and show the testing interface
    tester = NotificationTestingInterface()
    tester.show()

    # Add some welcome notifications
    notify_system("Testing Interface Ready", "Enhanced notification system testing interface is now ready!", "Test Interface")
    notify_info("Improved Spacing", "All notifications now have better spacing and visibility!", "Test Interface")

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
