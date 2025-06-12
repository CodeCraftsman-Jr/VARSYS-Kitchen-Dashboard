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
    """Bell icon widget with notification count badge"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notification_count = 0
        self.unread_count = 0
        self.notifications = []
        self.notification_panel = None
        
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
        
        # Bell color based on notifications
        if self.unread_count > 0:
            bell_color = QColor("#f39c12")  # Orange for unread
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
    
    def add_notification(self, title, message, notification_type="info"):
        """Add a new notification"""
        notification = {
            'id': len(self.notifications) + 1,
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        self.notifications.insert(0, notification)  # Add to beginning
        self.unread_count += 1
        self.notification_count += 1
        
        # Limit to 100 notifications
        if len(self.notifications) > 100:
            self.notifications = self.notifications[:100]
        
        # Update display
        self.update()
        
        # Update panel if visible
        if self.notification_panel and self.notification_panel.isVisible():
            self.notification_panel.refresh_notifications(self.notifications)
        
        # Save notifications
        self.save_notifications()
        
        return notification
    
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
    """Notification panel that shows when bell is clicked"""
    
    notification_read = Signal(int)
    clear_all = Signal()
    
    def __init__(self, notifications, parent=None):
        super().__init__(parent)
        self.notifications = notifications
        self.init_ui()
        
        # Set window flags
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def init_ui(self):
        """Initialize the panel UI"""
        self.setFixedSize(300, 400)
        
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
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.setSpacing(5)
        
        scroll_area.setWidget(self.notifications_widget)
        frame_layout.addWidget(scroll_area)
        
        layout.addWidget(main_frame)
        
        # Populate notifications
        self.refresh_notifications(self.notifications)
    
    def refresh_notifications(self, notifications):
        """Refresh the notifications display"""
        # Clear existing notifications
        for i in reversed(range(self.notifications_layout.count())):
            child = self.notifications_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add notifications
        if not notifications:
            no_notifications = QLabel("No notifications")
            no_notifications.setAlignment(Qt.AlignCenter)
            no_notifications.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
            self.notifications_layout.addWidget(no_notifications)
        else:
            for notification in notifications:
                notification_widget = self.create_notification_widget(notification)
                self.notifications_layout.addWidget(notification_widget)
        
        self.notifications_layout.addStretch()
    
    def create_notification_widget(self, notification):
        """Create a widget for a single notification"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        
        # Style based on read status
        if notification.get('read', False):
            bg_color = "#f8f9fa"
            border_color = "#e9ecef"
        else:
            bg_color = "#fff3cd"
            border_color = "#ffeaa7"
        
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(3)
        
        # Title and timestamp
        header_layout = QHBoxLayout()
        
        title_label = QLabel(notification['title'])
        title_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Timestamp
        timestamp = datetime.fromisoformat(notification['timestamp'])
        time_str = timestamp.strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(notification['message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #34495e; font-size: 12px;")
        layout.addWidget(message_label)
        
        # Mark as read on click
        widget.mousePressEvent = lambda event, nid=notification['id']: self.notification_read.emit(nid)
        widget.setCursor(Qt.PointingHandCursor)
        
        return widget
