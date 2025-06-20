#!/usr/bin/env python3
"""
Advanced Notification System Features
Adds sophisticated functionality to the enhanced notification system
"""

import sys
import os
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    print("⚠️ PySide6 not available - GUI features disabled")

from modules.enhanced_notification_system import get_notification_manager

class NotificationFrequency(Enum):
    """Notification frequency settings"""
    IMMEDIATE = "immediate"
    BATCHED_5MIN = "batched_5min"
    BATCHED_15MIN = "batched_15min"
    BATCHED_HOURLY = "batched_hourly"
    DAILY_DIGEST = "daily_digest"

class NotificationAction(Enum):
    """Available notification actions"""
    DISMISS = "dismiss"
    SNOOZE = "snooze"
    MARK_READ = "mark_read"
    ARCHIVE = "archive"
    ESCALATE = "escalate"
    FORWARD = "forward"

@dataclass
class NotificationRule:
    """Advanced notification rule configuration"""
    category: str
    priority_threshold: int
    frequency: NotificationFrequency
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    weekend_enabled: bool = True
    escalation_delay_minutes: int = 30
    max_notifications_per_hour: int = 10
    keywords_filter: List[str] = None
    source_filter: List[str] = None
    enabled: bool = True

class AdvancedNotificationManager:
    """Advanced notification management with sophisticated features"""
    
    def __init__(self):
        self.base_manager = get_notification_manager()
        self.rules: Dict[str, NotificationRule] = {}
        self.notification_history: List[Dict] = []
        self.user_preferences = self.load_user_preferences()
        self.analytics_data = {
            'total_sent': 0,
            'total_read': 0,
            'total_dismissed': 0,
            'category_stats': {},
            'hourly_stats': {},
            'response_times': []
        }
        self.setup_default_rules()
        
    def setup_default_rules(self):
        """Setup intelligent default notification rules"""
        default_rules = [
            NotificationRule(
                category="emergency",
                priority_threshold=1,
                frequency=NotificationFrequency.IMMEDIATE,
                quiet_hours_start="00:00",  # Always immediate for emergencies
                quiet_hours_end="00:00",
                max_notifications_per_hour=100
            ),
            NotificationRule(
                category="critical",
                priority_threshold=2,
                frequency=NotificationFrequency.IMMEDIATE,
                max_notifications_per_hour=20
            ),
            NotificationRule(
                category="error",
                priority_threshold=3,
                frequency=NotificationFrequency.BATCHED_5MIN,
                max_notifications_per_hour=15
            ),
            NotificationRule(
                category="info",
                priority_threshold=10,
                frequency=NotificationFrequency.BATCHED_15MIN,
                max_notifications_per_hour=5
            ),
            NotificationRule(
                category="success",
                priority_threshold=11,
                frequency=NotificationFrequency.BATCHED_HOURLY,
                max_notifications_per_hour=3
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.category] = rule
    
    def load_user_preferences(self) -> Dict:
        """Load user notification preferences"""
        prefs_file = "notification_preferences.json"
        default_prefs = {
            "sound_enabled": True,
            "desktop_notifications": True,
            "email_notifications": False,
            "sms_notifications": False,
            "do_not_disturb_enabled": False,
            "theme": "auto",  # auto, light, dark
            "animation_enabled": True,
            "compact_mode": False,
            "auto_dismiss_success": True,
            "auto_dismiss_delay": 5000,
            "notification_position": "top_right",
            "max_visible_notifications": 5
        }
        
        try:
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r') as f:
                    saved_prefs = json.load(f)
                    default_prefs.update(saved_prefs)
        except Exception as e:
            print(f"⚠️ Could not load preferences: {e}")
        
        return default_prefs
    
    def save_user_preferences(self):
        """Save user notification preferences"""
        try:
            with open("notification_preferences.json", 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save preferences: {e}")
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours"""
        if self.user_preferences.get("do_not_disturb_enabled", False):
            return True
            
        now = datetime.now().time()
        # This is a simplified check - in production you'd want more sophisticated logic
        return False
    
    def should_send_notification(self, category: str, priority: int, source: str = None) -> bool:
        """Intelligent decision on whether to send notification"""
        rule = self.rules.get(category)
        if not rule or not rule.enabled:
            return False
        
        # Check priority threshold
        if priority > rule.priority_threshold:
            return False
        
        # Check quiet hours (except for emergencies)
        if category != "emergency" and self.is_quiet_hours():
            return False
        
        # Check rate limiting
        current_hour = datetime.now().hour
        hour_key = f"{datetime.now().date()}_{current_hour}"
        hourly_count = self.analytics_data['hourly_stats'].get(hour_key, 0)
        
        if hourly_count >= rule.max_notifications_per_hour:
            return False
        
        # Check source filter
        if rule.source_filter and source and source not in rule.source_filter:
            return False
        
        return True
    
    def send_smart_notification(self, title: str, message: str, category: str = "info", 
                              priority: int = 10, source: str = "System", **kwargs):
        """Send notification with intelligent processing"""
        
        # Check if notification should be sent
        if not self.should_send_notification(category, priority, source):
            self.queue_notification(title, message, category, priority, source, **kwargs)
            return False
        
        # Update analytics
        self.update_analytics(category, priority, source)
        
        # Send through base manager
        result = self.base_manager.notify(
            title=title,
            message=message,
            category=category,
            priority=priority,
            source=source,
            **kwargs
        )
        
        # Store in history
        self.notification_history.append({
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'category': category,
            'priority': priority,
            'source': source,
            'sent': True
        })
        
        return result
    
    def queue_notification(self, title: str, message: str, category: str, 
                          priority: int, source: str, **kwargs):
        """Queue notification for batch processing"""
        # In a full implementation, this would add to a queue for later processing
        self.notification_history.append({
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'category': category,
            'priority': priority,
            'source': source,
            'sent': False,
            'queued': True
        })
    
    def update_analytics(self, category: str, priority: int, source: str):
        """Update notification analytics"""
        self.analytics_data['total_sent'] += 1
        
        # Category stats
        if category not in self.analytics_data['category_stats']:
            self.analytics_data['category_stats'][category] = 0
        self.analytics_data['category_stats'][category] += 1
        
        # Hourly stats
        current_hour = datetime.now().hour
        hour_key = f"{datetime.now().date()}_{current_hour}"
        if hour_key not in self.analytics_data['hourly_stats']:
            self.analytics_data['hourly_stats'][hour_key] = 0
        self.analytics_data['hourly_stats'][hour_key] += 1
    
    def get_analytics_summary(self) -> Dict:
        """Get comprehensive analytics summary"""
        total_notifications = len(self.notification_history)
        sent_notifications = len([n for n in self.notification_history if n.get('sent', False)])
        queued_notifications = len([n for n in self.notification_history if n.get('queued', False)])
        
        # Calculate response rates
        read_rate = (self.analytics_data['total_read'] / max(sent_notifications, 1)) * 100
        dismiss_rate = (self.analytics_data['total_dismissed'] / max(sent_notifications, 1)) * 100
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_notifications = [
            n for n in self.notification_history 
            if datetime.fromisoformat(n['timestamp']) > recent_cutoff
        ]
        
        return {
            'total_notifications': total_notifications,
            'sent_notifications': sent_notifications,
            'queued_notifications': queued_notifications,
            'read_rate_percent': round(read_rate, 1),
            'dismiss_rate_percent': round(dismiss_rate, 1),
            'recent_24h_count': len(recent_notifications),
            'category_breakdown': self.analytics_data['category_stats'].copy(),
            'most_active_category': max(
                self.analytics_data['category_stats'].items(), 
                key=lambda x: x[1], 
                default=('none', 0)
            )[0],
            'average_per_hour': round(sent_notifications / max(len(self.analytics_data['hourly_stats']), 1), 1)
        }

class NotificationPreferencesDialog(QDialog):
    """Advanced preferences dialog for notification settings"""
    
    def __init__(self, advanced_manager: AdvancedNotificationManager, parent=None):
        super().__init__(parent)
        self.advanced_manager = advanced_manager
        self.setWindowTitle("🔔 Advanced Notification Preferences")
        self.setFixedSize(600, 700)
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the preferences UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔔 Notification Preferences")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2563eb; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f3f4f6;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #2563eb;
                color: white;
            }
        """)
        
        # General tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "🔧 General")
        
        # Rules tab
        rules_tab = self.create_rules_tab()
        tab_widget.addTab(rules_tab, "📋 Rules")
        
        # Analytics tab
        analytics_tab = self.create_analytics_tab()
        tab_widget.addTab(analytics_tab, "📊 Analytics")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self) -> QWidget:
        """Create general preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Sound settings
        sound_group = QGroupBox("🔊 Sound Settings")
        sound_layout = QVBoxLayout(sound_group)
        
        self.sound_enabled = QCheckBox("Enable notification sounds")
        sound_layout.addWidget(self.sound_enabled)
        
        layout.addWidget(sound_group)
        
        # Display settings
        display_group = QGroupBox("🖥️ Display Settings")
        display_layout = QVBoxLayout(display_group)
        
        self.desktop_notifications = QCheckBox("Show desktop notifications")
        self.animation_enabled = QCheckBox("Enable animations")
        self.compact_mode = QCheckBox("Compact mode")
        
        display_layout.addWidget(self.desktop_notifications)
        display_layout.addWidget(self.animation_enabled)
        display_layout.addWidget(self.compact_mode)
        
        layout.addWidget(display_group)
        
        # Auto-dismiss settings
        dismiss_group = QGroupBox("⏰ Auto-Dismiss Settings")
        dismiss_layout = QVBoxLayout(dismiss_group)
        
        self.auto_dismiss_success = QCheckBox("Auto-dismiss success notifications")
        dismiss_layout.addWidget(self.auto_dismiss_success)
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Auto-dismiss delay (seconds):"))
        self.auto_dismiss_delay = QSpinBox()
        self.auto_dismiss_delay.setRange(1, 60)
        self.auto_dismiss_delay.setValue(5)
        delay_layout.addWidget(self.auto_dismiss_delay)
        delay_layout.addStretch()
        
        dismiss_layout.addLayout(delay_layout)
        layout.addWidget(dismiss_group)
        
        layout.addStretch()
        return widget
    
    def create_rules_tab(self) -> QWidget:
        """Create notification rules tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("📋 Configure notification rules for different categories")
        info_label.setStyleSheet("color: #6b7280; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Rules will be populated dynamically
        rules_scroll = QScrollArea()
        rules_widget = QWidget()
        self.rules_layout = QVBoxLayout(rules_widget)
        
        # Add rule widgets for each category
        for category, rule in self.advanced_manager.rules.items():
            rule_widget = self.create_rule_widget(category, rule)
            self.rules_layout.addWidget(rule_widget)
        
        rules_scroll.setWidget(rules_widget)
        rules_scroll.setWidgetResizable(True)
        layout.addWidget(rules_scroll)
        
        return widget
    
    def create_rule_widget(self, category: str, rule: NotificationRule) -> QWidget:
        """Create a widget for configuring a notification rule"""
        widget = QGroupBox(f"📂 {category.title()} Notifications")
        layout = QVBoxLayout(widget)
        
        # Enable/disable checkbox
        enabled_cb = QCheckBox("Enable notifications for this category")
        enabled_cb.setChecked(rule.enabled)
        layout.addWidget(enabled_cb)
        
        # Priority threshold
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priority threshold:"))
        priority_spin = QSpinBox()
        priority_spin.setRange(1, 20)
        priority_spin.setValue(rule.priority_threshold)
        priority_layout.addWidget(priority_spin)
        priority_layout.addStretch()
        layout.addLayout(priority_layout)
        
        # Max notifications per hour
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Max per hour:"))
        max_spin = QSpinBox()
        max_spin.setRange(1, 100)
        max_spin.setValue(rule.max_notifications_per_hour)
        max_layout.addWidget(max_spin)
        max_layout.addStretch()
        layout.addLayout(max_layout)
        
        return widget
    
    def create_analytics_tab(self) -> QWidget:
        """Create analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Get analytics data
        analytics = self.advanced_manager.get_analytics_summary()
        
        # Analytics display
        analytics_text = QTextEdit()
        analytics_text.setReadOnly(True)
        analytics_text.setMaximumHeight(400)
        
        analytics_content = f"""
📊 NOTIFICATION ANALYTICS SUMMARY

📈 Overall Statistics:
   • Total Notifications: {analytics['total_notifications']}
   • Successfully Sent: {analytics['sent_notifications']}
   • Queued/Pending: {analytics['queued_notifications']}
   • Read Rate: {analytics['read_rate_percent']}%
   • Dismiss Rate: {analytics['dismiss_rate_percent']}%

⏰ Recent Activity:
   • Last 24 Hours: {analytics['recent_24h_count']} notifications
   • Average per Hour: {analytics['average_per_hour']}
   • Most Active Category: {analytics['most_active_category']}

📂 Category Breakdown:
"""
        
        for category, count in analytics['category_breakdown'].items():
            analytics_content += f"   • {category.title()}: {count} notifications\n"
        
        analytics_text.setPlainText(analytics_content)
        analytics_text.setStyleSheet("""
            QTextEdit {
                background: #f8fafc;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(analytics_text)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Analytics")
        refresh_btn.clicked.connect(lambda: self.refresh_analytics(analytics_text))
        layout.addWidget(refresh_btn)
        
        return widget
    
    def refresh_analytics(self, text_widget: QTextEdit):
        """Refresh analytics display"""
        analytics = self.advanced_manager.get_analytics_summary()
        # Update the text widget with fresh data
        # (Implementation would update the content)
        text_widget.setPlainText("📊 Analytics refreshed at " + datetime.now().strftime("%H:%M:%S"))
    
    def load_current_settings(self):
        """Load current settings into the UI"""
        prefs = self.advanced_manager.user_preferences
        
        self.sound_enabled.setChecked(prefs.get('sound_enabled', True))
        self.desktop_notifications.setChecked(prefs.get('desktop_notifications', True))
        self.animation_enabled.setChecked(prefs.get('animation_enabled', True))
        self.compact_mode.setChecked(prefs.get('compact_mode', False))
        self.auto_dismiss_success.setChecked(prefs.get('auto_dismiss_success', True))
        self.auto_dismiss_delay.setValue(prefs.get('auto_dismiss_delay', 5000) // 1000)
    
    def save_settings(self):
        """Save the current settings"""
        prefs = self.advanced_manager.user_preferences
        
        prefs['sound_enabled'] = self.sound_enabled.isChecked()
        prefs['desktop_notifications'] = self.desktop_notifications.isChecked()
        prefs['animation_enabled'] = self.animation_enabled.isChecked()
        prefs['compact_mode'] = self.compact_mode.isChecked()
        prefs['auto_dismiss_success'] = self.auto_dismiss_success.isChecked()
        prefs['auto_dismiss_delay'] = self.auto_dismiss_delay.value() * 1000
        
        self.advanced_manager.save_user_preferences()
        
        QMessageBox.information(self, "Settings Saved", "✅ Your notification preferences have been saved successfully!")
        self.accept()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "🔄 Are you sure you want to reset all notification settings to defaults?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.advanced_manager.user_preferences = self.advanced_manager.load_user_preferences()
            self.advanced_manager.setup_default_rules()
            self.load_current_settings()
            
            QMessageBox.information(self, "Settings Reset", "✅ All settings have been reset to defaults!")

def create_advanced_notification_demo():
    """Create a demonstration of advanced notification features"""
    print("🚀 Advanced Notification System Demo")
    print("=" * 50)
    
    # Initialize advanced manager
    advanced_manager = AdvancedNotificationManager()
    
    # Send some test notifications
    test_notifications = [
        ("🚨 Critical System Alert", "Database connection lost", "critical", 1),
        ("📦 Inventory Update", "Stock levels updated successfully", "inventory", 8),
        ("✅ Backup Complete", "Daily backup completed successfully", "success", 11),
        ("⚠️ Low Stock Warning", "Tomatoes running low (5 units remaining)", "inventory", 7),
        ("🔧 Maintenance Required", "Kitchen equipment needs servicing", "maintenance", 6),
    ]
    
    print("📤 Sending test notifications with intelligent processing...")
    
    for title, message, category, priority in test_notifications:
        result = advanced_manager.send_smart_notification(
            title=title,
            message=message,
            category=category,
            priority=priority,
            source="Demo System"
        )
        
        status = "✅ Sent" if result else "⏸️ Queued"
        print(f"  {status}: {title}")
    
    # Show analytics
    print("\n📊 Analytics Summary:")
    analytics = advanced_manager.get_analytics_summary()
    for key, value in analytics.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    return advanced_manager

if __name__ == "__main__":
    # Run the demo
    advanced_manager = create_advanced_notification_demo()
    
    # If GUI is available, show preferences dialog
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("\n🎮 Opening Advanced Preferences Dialog...")
        dialog = NotificationPreferencesDialog(advanced_manager)
        dialog.show()
        
        if not app.exec():
            sys.exit(0)
            
    except Exception as e:
        print(f"⚠️ GUI not available: {e}")
        print("✅ Advanced notification system demo completed successfully!")
