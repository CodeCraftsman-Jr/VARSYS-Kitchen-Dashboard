#!/usr/bin/env python3
"""
Enhanced Notification System with Bell Icon
Provides bell icon notification system with history and persistence
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class NotificationBellWidget(QWidget):
    """Enhanced bell icon widget with notification count badge and categorization"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notification_count = 0
        self.unread_count = 0
        self.notifications = []
        self.notification_panel = None

        # Enhanced notification categories with priorities, colors, and comprehensive coverage
        self.categories = {
            # Critical Level (Priority 1-2)
            'critical': {'priority': 1, 'color': '#e74c3c', 'icon': '🚨', 'sound': True, 'persist': True},
            'emergency': {'priority': 1, 'color': '#c0392b', 'icon': '🆘', 'sound': True, 'persist': True},
            'security': {'priority': 2, 'color': '#8e44ad', 'icon': '🔒', 'sound': True, 'persist': True},

            # Error Level (Priority 3-4)
            'error': {'priority': 3, 'color': '#e74c3c', 'icon': '❌', 'sound': False, 'persist': True},
            'failure': {'priority': 4, 'color': '#c0392b', 'icon': '💥', 'sound': False, 'persist': True},

            # Warning Level (Priority 5-7)
            'warning': {'priority': 5, 'color': '#f39c12', 'icon': '⚠️', 'sound': False, 'persist': False},
            'maintenance': {'priority': 6, 'color': '#e67e22', 'icon': '🔧', 'sound': False, 'persist': False},
            'resource': {'priority': 7, 'color': '#d35400', 'icon': '📊', 'sound': False, 'persist': False},

            # Operational Level (Priority 8-10)
            'inventory': {'priority': 8, 'color': '#3498db', 'icon': '📦', 'sound': False, 'persist': False},
            'staff': {'priority': 8, 'color': '#2980b9', 'icon': '👥', 'sound': False, 'persist': False},
            'schedule': {'priority': 9, 'color': '#1abc9c', 'icon': '📅', 'sound': False, 'persist': False},
            'budget': {'priority': 9, 'color': '#16a085', 'icon': '💰', 'sound': False, 'persist': False},
            'recipe': {'priority': 10, 'color': '#27ae60', 'icon': '🍳', 'sound': False, 'persist': False},

            # Success Level (Priority 11-12)
            'success': {'priority': 11, 'color': '#27ae60', 'icon': '✅', 'sound': False, 'persist': False},
            'completion': {'priority': 12, 'color': '#2ecc71', 'icon': '🎉', 'sound': False, 'persist': False},

            # Information Level (Priority 13-15)
            'info': {'priority': 13, 'color': '#3498db', 'icon': 'ℹ️', 'sound': False, 'persist': False},
            'update': {'priority': 14, 'color': '#2980b9', 'icon': '🔄', 'sound': False, 'persist': False},
            'sync': {'priority': 14, 'color': '#3498db', 'icon': '🔄', 'sound': False, 'persist': False},

            # System Level (Priority 16-18)
            'system': {'priority': 16, 'color': '#9b59b6', 'icon': '⚙️', 'sound': False, 'persist': False},
            'startup': {'priority': 17, 'color': '#8e44ad', 'icon': '🚀', 'sound': False, 'persist': False},
            'debug': {'priority': 18, 'color': '#95a5a6', 'icon': '🐛', 'sound': False, 'persist': False}
        }

        # Load existing notifications
        self.load_notifications()

        # Set up UI
        self.init_ui()

        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_notifications)
        self.save_timer.start(30000)  # Save every 30 seconds
    
    def init_ui(self):
        """Initialize the bell icon UI"""
        self.setFixedSize(50, 40)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set tooltip
        self.setToolTip("Click to view notifications")
        
        # Connect click event
        self.mousePressEvent = self.on_bell_clicked
    
    def paintEvent(self, event):
        """Custom paint event to draw bell icon and badge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw bell icon
        bell_rect = QRect(10, 8, 24, 24)
        
        # Enhanced bell color based on highest priority notification
        if self.unread_count > 0:
            highest_priority_category = self.get_highest_priority_category()
            if highest_priority_category:
                category_info = self.categories.get(highest_priority_category, {})
                bell_color = QColor(category_info.get('color', '#f39c12'))
            else:
                bell_color = QColor("#f39c12")  # Default orange for unread
        else:
            bell_color = QColor("#7f8c8d")  # Gray for no unread
        
        painter.setBrush(QBrush(bell_color))
        painter.setPen(QPen(bell_color, 2))
        
        # Draw bell shape (simplified)
        painter.drawEllipse(bell_rect.adjusted(2, 2, -2, -6))
        painter.drawRect(bell_rect.adjusted(8, 22, -8, -2))
        
        # Draw notification badge if there are unread notifications
        if self.unread_count > 0:
            badge_rect = QRect(28, 5, 16, 16)
            
            # Badge background
            painter.setBrush(QBrush(QColor("#e74c3c")))
            painter.setPen(QPen(QColor("#e74c3c")))
            painter.drawEllipse(badge_rect)
            
            # Badge text
            painter.setPen(QPen(QColor("white")))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            
            count_text = str(min(self.unread_count, 99))  # Max 99
            if self.unread_count > 99:
                count_text = "99+"
            
            painter.drawText(badge_rect, Qt.AlignCenter, count_text)
    
    def on_bell_clicked(self, event):
        """Handle bell icon click"""
        if event.button() == Qt.LeftButton:
            self.show_notification_panel()
    
    def show_notification_panel(self):
        """Show/hide the notification panel"""
        if self.notification_panel is None:
            self.notification_panel = NotificationPanel(self.notifications, self)
            self.notification_panel.notification_read.connect(self.mark_notification_read)
            self.notification_panel.clear_all.connect(self.clear_all_notifications)
        
        # Position panel below the bell
        global_pos = self.mapToGlobal(QPoint(0, self.height()))
        self.notification_panel.move(global_pos.x() - 250, global_pos.y())
        
        if self.notification_panel.isVisible():
            self.notification_panel.hide()
        else:
            self.notification_panel.show()
            self.notification_panel.raise_()
            self.notification_panel.activateWindow()
    
    def add_notification(self, title, message, notification_type="info", category=None, priority=None, source=None):
        """Add a new notification with enhanced categorization"""
        # Validate and set category
        if category and category not in self.categories:
            category = notification_type  # Fallback to type
        if not category:
            category = notification_type

        # Auto-detect category based on keywords if not specified
        if category == notification_type and notification_type == "info":
            category = self.auto_detect_category(title, message)

        # Generate unique ID
        notification_id = int(datetime.now().timestamp() * 1000)

        notification = {
            'id': notification_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'category': category,
            'priority': priority or self.categories.get(category, {}).get('priority', 5),
            'source': source or 'System',
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'icon': self.categories.get(category, {}).get('icon', 'ℹ️'),
            'color': self.categories.get(category, {}).get('color', '#3498db')
        }

        # Insert based on priority (higher priority = lower number = first)
        inserted = False
        for i, existing in enumerate(self.notifications):
            if notification['priority'] < existing.get('priority', 5):
                self.notifications.insert(i, notification)
                inserted = True
                break

        if not inserted:
            self.notifications.append(notification)

        self.unread_count += 1
        self.notification_count += 1

        # Limit to 200 notifications (increased for better history)
        if len(self.notifications) > 200:
            # Remove oldest read notifications first
            read_notifications = [n for n in self.notifications if n.get('read', False)]
            if read_notifications:
                # Remove oldest read notification
                oldest_read = max(read_notifications, key=lambda x: x['timestamp'])
                self.notifications.remove(oldest_read)
            else:
                # Remove oldest notification if all are unread
                self.notifications = self.notifications[:200]

        # Handle sound notifications for critical categories
        category_info = self.categories.get(category, {})
        if category_info.get('sound', False):
            self.play_notification_sound(category)

        # Handle persistent notifications (don't auto-dismiss)
        if category_info.get('persist', False):
            notification['persistent'] = True

        # Update display
        self.update()

        # Update panel if visible
        if self.notification_panel and self.notification_panel.isVisible():
            self.notification_panel.refresh_notifications(self.notifications)

        # Save notifications
        self.save_notifications()

        # Enhanced logging with category and priority
        priority = notification.get('priority', 5)
        icon = notification.get('icon', 'ℹ️')
        print(f"📢 {icon} {category.upper()} (P{priority}): {title} - {message}")

        return notification

    def auto_detect_category(self, title, message):
        """Enhanced auto-detect notification category based on content with comprehensive keyword matching"""
        content = f"{title} {message}".lower()

        # Emergency/Critical keywords (Priority 1-2)
        if any(word in content for word in ['emergency', 'sos', 'help', 'urgent critical', 'immediate attention']):
            return 'emergency'
        if any(word in content for word in ['security breach', 'unauthorized', 'hack', 'intrusion', 'breach']):
            return 'security'
        if any(word in content for word in ['critical', 'urgent', 'crash', 'fatal', 'down', 'offline']):
            return 'critical'

        # Error/Failure keywords (Priority 3-4)
        if any(word in content for word in ['failure', 'failed to start', 'system failure', 'connection failed']):
            return 'failure'
        if any(word in content for word in ['error', 'failed', 'exception', 'invalid', 'corrupt', 'broken']):
            return 'error'

        # Warning/Maintenance keywords (Priority 5-7)
        if any(word in content for word in ['maintenance', 'scheduled', 'repair', 'service', 'cleaning']):
            return 'maintenance'
        if any(word in content for word in ['low stock', 'running low', 'shortage', 'resource', 'capacity']):
            return 'resource'
        if any(word in content for word in ['warning', 'caution', 'expired', 'missing', 'duplicate', 'attention']):
            return 'warning'

        # Operational keywords (Priority 8-10)
        if any(word in content for word in ['inventory', 'stock', 'item', 'ingredient', 'supply']):
            return 'inventory'
        if any(word in content for word in ['staff', 'employee', 'team', 'assignment', 'shift']):
            return 'staff'
        if any(word in content for word in ['schedule', 'calendar', 'appointment', 'meeting', 'event']):
            return 'schedule'
        if any(word in content for word in ['budget', 'expense', 'cost', 'payment', 'financial']):
            return 'budget'
        if any(word in content for word in ['recipe', 'cooking', 'preparation', 'ingredient', 'meal']):
            return 'recipe'

        # Success/Completion keywords (Priority 11-12)
        if any(word in content for word in ['completed', 'finished', 'done', 'accomplished', 'achieved']):
            return 'completion'
        if any(word in content for word in ['success', 'successful', 'saved', 'created', 'added']):
            return 'success'

        # Information/Update keywords (Priority 13-15)
        if any(word in content for word in ['sync', 'synchronized', 'syncing', 'backup', 'restore']):
            return 'sync'
        if any(word in content for word in ['update', 'updated', 'upgrade', 'version', 'patch']):
            return 'update'

        # System keywords (Priority 16-18)
        if any(word in content for word in ['debug', 'trace', 'log', 'diagnostic']):
            return 'debug'
        if any(word in content for word in ['startup', 'initialization', 'boot', 'launch', 'start']):
            return 'startup'
        if any(word in content for word in ['system', 'configuration', 'settings', 'service']):
            return 'system'

        return 'info'  # Default

    def play_notification_sound(self, category):
        """Play notification sound for critical categories"""
        try:
            # Try to play system sound (Windows)
            import winsound
            if category in ['critical', 'emergency', 'security']:
                # Critical sound - system exclamation
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif category in ['error', 'failure']:
                # Error sound - system hand
                winsound.MessageBeep(winsound.MB_ICONHAND)
        except ImportError:
            try:
                # Try cross-platform sound
                import pygame
                pygame.mixer.init()
                # You can add custom sound files here
                print(f"🔊 Sound notification for {category}")
            except ImportError:
                # Fallback - just print
                print(f"🔊 Sound notification for {category} (no audio system available)")
        except Exception as e:
            print(f"Error playing notification sound: {e}")

    def get_highest_priority_category(self):
        """Get the category of the highest priority unread notification"""
        unread_notifications = [n for n in self.notifications if not n.get('read', False)]
        if not unread_notifications:
            return None

        highest_priority = min(n.get('priority', 5) for n in unread_notifications)
        for notification in unread_notifications:
            if notification.get('priority', 5) == highest_priority:
                return notification.get('category', 'info')
        return 'info'
    
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification['id'] == notification_id and not notification['read']:
                notification['read'] = True
                self.unread_count = max(0, self.unread_count - 1)
                break
        
        self.update()
        self.save_notifications()
    
    def clear_all_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()
        self.unread_count = 0
        self.notification_count = 0
        self.update()
        self.save_notifications()
        
        if self.notification_panel:
            self.notification_panel.refresh_notifications(self.notifications)
    
    def load_notifications(self):
        """Load notifications from file"""
        try:
            notifications_file = 'data/notifications.json'
            if os.path.exists(notifications_file):
                with open(notifications_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notifications = data.get('notifications', [])
                    
                    # Count unread notifications
                    self.unread_count = sum(1 for n in self.notifications if not n.get('read', False))
                    self.notification_count = len(self.notifications)
        except Exception as e:
            print(f"Error loading notifications: {e}")
            self.notifications = []
            self.unread_count = 0
            self.notification_count = 0
    
    def save_notifications(self):
        """Save notifications to file"""
        try:
            os.makedirs('data', exist_ok=True)
            notifications_file = 'data/notifications.json'
            
            data = {
                'notifications': self.notifications,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(notifications_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving notifications: {e}")


class NotificationPanel(QWidget):
    """Enhanced notification panel with categorization and filtering"""

    notification_read = Signal(int)
    clear_all = Signal()

    def __init__(self, notifications, parent=None):
        super().__init__(parent)
        self.notifications = notifications
        self.current_filter = 'all'  # all, unread, critical, error, warning, success, info, system
        self.init_ui()

        # Set window flags
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def init_ui(self):
        """Initialize the panel UI"""
        self.setFixedSize(450, 550)  # Increased size for better visibility
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Create main frame
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Box)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }
        """)
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Notifications")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Clear all button
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_all.emit)
        header_layout.addWidget(clear_btn)
        
        frame_layout.addLayout(header_layout)

        # Category filter buttons
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)

        # Filter buttons for major categories
        filter_categories = [
            ('All', 'all', '#95a5a6'),
            ('Critical', 'critical', '#e74c3c'),
            ('Errors', 'error', '#e74c3c'),
            ('Warnings', 'warning', '#f39c12'),
            ('Operations', 'operational', '#3498db'),
            ('Success', 'success', '#27ae60')
        ]

        self.filter_buttons = {}
        for name, category, color in filter_categories:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    border: 2px solid #2c3e50;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            btn.clicked.connect(lambda checked, cat=category: self.set_filter(cat))
            self.filter_buttons[category] = btn
            filter_layout.addWidget(btn)

        # Set 'All' as default
        self.filter_buttons['all'].setChecked(True)
        filter_layout.addStretch()

        frame_layout.addLayout(filter_layout)

        # Notifications scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Notifications widget
        self.notifications_widget = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_widget)
        self.notifications_layout.setContentsMargins(8, 8, 8, 8)  # Add margins around notifications
        self.notifications_layout.setSpacing(12)  # Increased spacing between notifications
        
        scroll_area.setWidget(self.notifications_widget)
        frame_layout.addWidget(scroll_area)
        
        layout.addWidget(main_frame)
        
        # Populate notifications
        self.refresh_notifications(self.notifications)

    def set_filter(self, category):
        """Set the notification filter"""
        # Uncheck all buttons
        for btn in self.filter_buttons.values():
            btn.setChecked(False)

        # Check the selected button
        if category in self.filter_buttons:
            self.filter_buttons[category].setChecked(True)

        self.current_filter = category
        self.refresh_notifications(self.notifications)

    def filter_notifications(self, notifications):
        """Filter notifications based on current filter"""
        if self.current_filter == 'all':
            return notifications
        elif self.current_filter == 'operational':
            # Group operational categories
            operational_categories = ['inventory', 'staff', 'schedule', 'budget', 'recipe']
            return [n for n in notifications if n.get('category') in operational_categories]
        else:
            # Filter by specific category or related categories
            if self.current_filter == 'critical':
                filter_categories = ['critical', 'emergency', 'security']
            elif self.current_filter == 'error':
                filter_categories = ['error', 'failure']
            elif self.current_filter == 'warning':
                filter_categories = ['warning', 'maintenance', 'resource']
            elif self.current_filter == 'success':
                filter_categories = ['success', 'completion']
            else:
                filter_categories = [self.current_filter]

            return [n for n in notifications if n.get('category') in filter_categories]
    
    def refresh_notifications(self, notifications):
        """Refresh the notifications display with filtering"""
        # Clear existing notifications
        for i in reversed(range(self.notifications_layout.count())):
            child = self.notifications_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Filter notifications
        filtered_notifications = self.filter_notifications(notifications)

        # Add notifications
        if not filtered_notifications:
            no_notifications = QLabel("No notifications in this category")
            no_notifications.setAlignment(Qt.AlignCenter)
            no_notifications.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
            self.notifications_layout.addWidget(no_notifications)
        else:
            for notification in filtered_notifications:
                notification_widget = self.create_notification_widget(notification)
                self.notifications_layout.addWidget(notification_widget)

        self.notifications_layout.addStretch()
    
    def create_notification_widget(self, notification):
        """Create an enhanced widget for a single notification"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setMinimumHeight(80)  # Set minimum height for better visibility

        # Enhanced styling based on category and read status
        category = notification.get('category', 'info')
        category_info = notification.get('color', '#3498db')

        if notification.get('read', False):
            bg_color = "#f8f9fa"
            border_color = "#e9ecef"
            opacity = "0.7"
        else:
            # Use category color for unread notifications
            if notification.get('priority', 5) <= 3:  # Critical/Error
                bg_color = "#fdf2f2"
                border_color = category_info
            elif notification.get('priority', 5) <= 7:  # Warning
                bg_color = "#fffbf0"
                border_color = category_info
            else:  # Info/Success
                bg_color = "#f0f9ff"
                border_color = category_info
            opacity = "1.0"

        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 5px;
                opacity: {opacity};
            }}
            QFrame:hover {{
                background-color: #e8f4fd;
                border-color: #3498db;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 12, 15, 12)  # Increased margins
        layout.setSpacing(8)  # Increased spacing between elements

        # Header with icon, title, priority, and timestamp
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)  # Add spacing between header elements

        # Category icon
        icon_label = QLabel(notification.get('icon', 'ℹ️'))
        icon_label.setStyleSheet("font-size: 18px; margin-right: 8px; min-width: 25px;")
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)

        # Title with priority indicator
        priority = notification.get('priority', 5)
        priority_indicator = "🔴" if priority <= 3 else "🟡" if priority <= 7 else "🟢"
        title_text = f"{priority_indicator} {notification['title']}"

        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px; padding: 2px 0px;")
        title_label.setWordWrap(True)  # Allow title to wrap if too long
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Source and timestamp
        source = notification.get('source', 'System')
        timestamp = datetime.fromisoformat(notification['timestamp'])
        time_str = timestamp.strftime("%H:%M")

        info_label = QLabel(f"{source} • {time_str}")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 2px 4px;")
        info_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(info_label)

        layout.addLayout(header_layout)

        # Message
        message_label = QLabel(notification['message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            color: #34495e;
            font-size: 13px;
            margin-left: 25px;
            margin-top: 4px;
            margin-bottom: 6px;
            line-height: 1.4;
            padding: 4px 0px;
        """)
        layout.addWidget(message_label)

        # Category tag
        category_tag = QLabel(f"#{category.upper()}")
        category_tag.setStyleSheet(f"""
            color: {category_info};
            font-size: 11px;
            font-weight: bold;
            margin-left: 25px;
            margin-top: 2px;
            padding: 2px 0px;
        """)
        layout.addWidget(category_tag)

        # Mark as read on click
        widget.mousePressEvent = lambda event, nid=notification['id']: self.notification_read.emit(nid)
        widget.setCursor(Qt.PointingHandCursor)

        return widget


class CentralizedNotificationManager:
    """Centralized notification management system"""

    def __init__(self):
        self.bell_widget = None
        self.toast_manager = None
        self.subscribers = []  # Components that want to receive notifications
        self.notification_history = []
        self.settings = {
            'enable_toast': True,
            'enable_bell': True,
            'enable_logging': True,
            'auto_categorize': True,
            'max_history': 500
        }

    def register_bell_widget(self, bell_widget):
        """Register the bell widget"""
        self.bell_widget = bell_widget
        print("📢 Bell widget registered with centralized manager")

    def register_toast_manager(self, toast_manager):
        """Register the toast notification manager"""
        self.toast_manager = toast_manager
        print("📢 Toast manager registered with centralized manager")

    def subscribe(self, component, categories=None):
        """Subscribe a component to receive notifications"""
        self.subscribers.append({
            'component': component,
            'categories': categories or ['all']
        })
        print(f"📢 Component subscribed to notifications: {categories or ['all']}")

    def notify(self, title, message, category='info', priority=None, source=None,
               show_toast=True, show_bell=True, duration=5000):
        """Send a notification through all registered channels"""

        # Create notification object
        notification = {
            'title': title,
            'message': message,
            'category': category,
            'priority': priority,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'id': int(datetime.now().timestamp() * 1000)
        }

        # Add to history
        self.notification_history.insert(0, notification)
        if len(self.notification_history) > self.settings['max_history']:
            self.notification_history = self.notification_history[:self.settings['max_history']]

        # Send to bell widget
        if show_bell and self.bell_widget and self.settings['enable_bell']:
            try:
                self.bell_widget.add_notification(title, message, category, category, priority, source)
            except Exception as e:
                print(f"Error sending to bell widget: {e}")

        # Send to toast manager
        if show_toast and self.toast_manager and self.settings['enable_toast']:
            try:
                self.toast_manager.show_notification(title, message, category, duration)
            except Exception as e:
                print(f"Error sending to toast manager: {e}")

        # Notify subscribers
        for subscriber in self.subscribers:
            if 'all' in subscriber['categories'] or category in subscriber['categories']:
                try:
                    if hasattr(subscriber['component'], 'on_notification'):
                        subscriber['component'].on_notification(notification)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")

        return notification

    def get_notifications(self, category=None, unread_only=False, limit=None):
        """Get notifications with optional filtering"""
        notifications = self.notification_history

        if category and category != 'all':
            notifications = [n for n in notifications if n.get('category') == category]

        if unread_only:
            notifications = [n for n in notifications if not n.get('read', False)]

        if limit:
            notifications = notifications[:limit]

        return notifications

    def mark_read(self, notification_id):
        """Mark a notification as read"""
        for notification in self.notification_history:
            if notification['id'] == notification_id:
                notification['read'] = True
                break

    def clear_category(self, category):
        """Clear all notifications of a specific category"""
        self.notification_history = [n for n in self.notification_history
                                   if n.get('category') != category]

    def get_stats(self):
        """Get notification statistics"""
        total = len(self.notification_history)
        unread = len([n for n in self.notification_history if not n.get('read', False)])

        categories = {}
        for notification in self.notification_history:
            cat = notification.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1

        return {
            'total': total,
            'unread': unread,
            'categories': categories
        }


# Global instance
_centralized_manager = None

def get_notification_manager():
    """Get the global centralized notification manager"""
    global _centralized_manager
    if _centralized_manager is None:
        _centralized_manager = CentralizedNotificationManager()
    return _centralized_manager

# Enhanced convenience functions for comprehensive notification categories
def notify_emergency(title, message, source=None, show_toast=True, show_bell=True):
    """Send emergency notification (highest priority)"""
    return get_notification_manager().notify(title, message, 'emergency', 1, source, show_toast, show_bell, 15000)

def notify_security(title, message, source=None, show_toast=True, show_bell=True):
    """Send security notification"""
    return get_notification_manager().notify(title, message, 'security', 2, source, show_toast, show_bell, 12000)

def notify_critical(title, message, source=None, show_toast=True, show_bell=True):
    """Send critical notification"""
    return get_notification_manager().notify(title, message, 'critical', 1, source, show_toast, show_bell, 10000)

def notify_error(title, message, source=None, show_toast=True, show_bell=True):
    """Send error notification"""
    return get_notification_manager().notify(title, message, 'error', 3, source, show_toast, show_bell, 8000)

def notify_failure(title, message, source=None, show_toast=True, show_bell=True):
    """Send failure notification"""
    return get_notification_manager().notify(title, message, 'failure', 4, source, show_toast, show_bell, 8000)

def notify_maintenance(title, message, source=None, show_toast=True, show_bell=True):
    """Send maintenance notification"""
    return get_notification_manager().notify(title, message, 'maintenance', 6, source, show_toast, show_bell, 6000)

def notify_resource(title, message, source=None, show_toast=True, show_bell=True):
    """Send resource warning notification"""
    return get_notification_manager().notify(title, message, 'resource', 7, source, show_toast, show_bell, 6000)

def notify_inventory(title, message, source=None, show_toast=True, show_bell=True):
    """Send inventory notification"""
    return get_notification_manager().notify(title, message, 'inventory', 8, source, show_toast, show_bell, 5000)

def notify_staff(title, message, source=None, show_toast=True, show_bell=True):
    """Send staff notification"""
    return get_notification_manager().notify(title, message, 'staff', 8, source, show_toast, show_bell, 5000)

def notify_schedule(title, message, source=None, show_toast=True, show_bell=True):
    """Send schedule notification"""
    return get_notification_manager().notify(title, message, 'schedule', 9, source, show_toast, show_bell, 5000)

def notify_budget(title, message, source=None, show_toast=True, show_bell=True):
    """Send budget notification"""
    return get_notification_manager().notify(title, message, 'budget', 9, source, show_toast, show_bell, 5000)

def notify_recipe(title, message, source=None, show_toast=True, show_bell=True):
    """Send recipe notification"""
    return get_notification_manager().notify(title, message, 'recipe', 10, source, show_toast, show_bell, 5000)

def notify_completion(title, message, source=None, show_toast=True, show_bell=True):
    """Send completion notification"""
    return get_notification_manager().notify(title, message, 'completion', 12, source, show_toast, show_bell, 4000)

def notify_sync(title, message, source=None, show_toast=True, show_bell=True):
    """Send sync notification"""
    return get_notification_manager().notify(title, message, 'sync', 14, source, show_toast, show_bell, 4000)

def notify_update(title, message, source=None, show_toast=True, show_bell=True):
    """Send update notification"""
    return get_notification_manager().notify(title, message, 'update', 14, source, show_toast, show_bell, 4000)

def notify_startup(title, message, source=None, show_toast=True, show_bell=True):
    """Send startup notification"""
    return get_notification_manager().notify(title, message, 'startup', 17, source, show_toast, show_bell, 3000)

def notify_debug(title, message, source=None, show_toast=True, show_bell=True):
    """Send debug notification"""
    return get_notification_manager().notify(title, message, 'debug', 18, source, show_toast, show_bell, 3000)

def notify_warning(title, message, source=None, show_toast=True, show_bell=True):
    """Send warning notification"""
    return get_notification_manager().notify(title, message, 'warning', 3, source, show_toast, show_bell, 6000)

def notify_success(title, message, source=None, show_toast=True, show_bell=True):
    """Send success notification"""
    return get_notification_manager().notify(title, message, 'success', 4, source, show_toast, show_bell, 4000)

def notify_info(title, message, source=None, show_toast=True, show_bell=True):
    """Send info notification"""
    return get_notification_manager().notify(title, message, 'info', 5, source, show_toast, show_bell, 5000)

def notify_system(title, message, source=None, show_toast=True, show_bell=True):
    """Send system notification"""
    return get_notification_manager().notify(title, message, 'system', 6, source, show_toast, show_bell, 3000)
