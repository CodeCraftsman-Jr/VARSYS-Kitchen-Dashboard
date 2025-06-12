"""
Notification System for Kitchen Dashboard
Provides toast notifications and system-wide notification management
"""

import sys
import logging
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QApplication, QGraphicsOpacityEffect)
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, Signal, Qt
from PySide6.QtGui import QFont, QPalette, QColor

class NotificationWidget(QFrame):
    """Individual notification widget"""
    
    closed = Signal(object)  # Signal emitted when notification is closed
    
    def __init__(self, title, message, notification_type="info", duration=5000, parent=None):
        super().__init__(parent)
        self.notification_type = notification_type
        self.duration = duration
        
        # Set up the widget
        self.setFixedSize(350, 80)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)
        
        # Set style based on notification type
        self.setup_style()
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Content layout
        content_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 9))
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
        """)
        close_button.clicked.connect(self.close_notification)
        
        layout.addLayout(content_layout)
        layout.addWidget(close_button, alignment=Qt.AlignTop)
        
        # Auto-close timer
        if duration > 0:
            self.timer = QTimer()
            self.timer.timeout.connect(self.close_notification)
            self.timer.start(duration)
        
        # Animation setup
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.hide)
        
        # Start fade in
        self.fade_in_animation.start()
    
    def setup_style(self):
        """Set up styling based on notification type"""
        styles = {
            "info": {
                "background": "#d1ecf1",
                "border": "#bee5eb",
                "color": "#0c5460"
            },
            "success": {
                "background": "#d4edda",
                "border": "#c3e6cb", 
                "color": "#155724"
            },
            "warning": {
                "background": "#fff3cd",
                "border": "#ffeaa7",
                "color": "#856404"
            },
            "error": {
                "background": "#f8d7da",
                "border": "#f5c6cb",
                "color": "#721c24"
            }
        }
        
        style = styles.get(self.notification_type, styles["info"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {style['background']};
                border: 2px solid {style['border']};
                border-radius: 8px;
                color: {style['color']};
            }}
            QLabel {{
                color: {style['color']};
                background: transparent;
                border: none;
            }}
        """)
    
    def close_notification(self):
        """Close the notification with fade out animation"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        self.fade_out_animation.finished.connect(lambda: self.closed.emit(self))
        self.fade_out_animation.start()


class NotificationManager(QWidget):
    """Manages and displays notifications"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.notifications = []
        
        # Set up the notification container
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Layout for notifications
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addStretch()  # Push notifications to bottom
        
        # Position the notification area
        self.position_notification_area()
        
        # Logger for notifications
        self.logger = logging.getLogger('NotificationManager')
    
    def position_notification_area(self):
        """Position the notification area in the bottom-right corner"""
        if self.parent_widget:
            parent_rect = self.parent_widget.geometry()
            self.setGeometry(
                parent_rect.right() - 370,
                parent_rect.top() + 50,
                360,
                parent_rect.height() - 100
            )
        else:
            # Fallback to screen geometry
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(
                screen.width() - 370,
                50,
                360,
                screen.height() - 100
            )
    
    def show_notification(self, title, message, notification_type="info", duration=5000):
        """Show a new notification"""
        # Log the notification in proper format (not the old NOTIFICATION format)
        log_message = f"{title}: {message}"
        if notification_type == "error":
            self.logger.error(log_message)
        elif notification_type == "warning":
            self.logger.warning(log_message)
        elif notification_type == "success":
            self.logger.info(log_message)
        else:
            self.logger.info(log_message)
        
        # Create notification widget
        notification = NotificationWidget(title, message, notification_type, duration, self)
        notification.closed.connect(self.remove_notification)
        
        # Add to layout (insert before stretch)
        self.layout.insertWidget(self.layout.count() - 1, notification)
        self.notifications.append(notification)
        
        # Show the notification area if hidden
        if not self.isVisible():
            self.show()
        
        # Limit number of notifications
        if len(self.notifications) > 5:
            oldest = self.notifications[0]
            oldest.close_notification()
        
        return notification
    
    def remove_notification(self, notification):
        """Remove a notification from the display"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.layout.removeWidget(notification)
            notification.deleteLater()
        
        # Hide notification area if no notifications
        if not self.notifications:
            self.hide()
    
    def clear_all_notifications(self):
        """Clear all notifications"""
        for notification in self.notifications[:]:
            notification.close_notification()
    
    def info(self, title, message, duration=5000):
        """Show info notification"""
        return self.show_notification(title, message, "info", duration)
    
    def success(self, title, message, duration=5000):
        """Show success notification"""
        return self.show_notification(title, message, "success", duration)
    
    def warning(self, title, message, duration=7000):
        """Show warning notification"""
        return self.show_notification(title, message, "warning", duration)
    
    def error(self, title, message, duration=10000):
        """Show error notification"""
        return self.show_notification(title, message, "error", duration)


# Global notification manager instance
_notification_manager = None

def get_notification_manager(parent=None):
    """Get or create the global notification manager"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager(parent)
    return _notification_manager

def show_notification(title, message, notification_type="info", duration=5000, parent=None):
    """Convenience function to show a notification"""
    manager = get_notification_manager(parent)
    return manager.show_notification(title, message, notification_type, duration)

def notify_info(title, message, duration=5000, parent=None):
    """Show info notification"""
    return show_notification(title, message, "info", duration, parent)

def notify_success(title, message, duration=5000, parent=None):
    """Show success notification"""
    return show_notification(title, message, "success", duration, parent)

def notify_warning(title, message, duration=7000, parent=None):
    """Show warning notification"""
    return show_notification(title, message, "warning", duration, parent)

def notify_error(title, message, duration=10000, parent=None):
    """Show error notification"""
    return show_notification(title, message, "error", duration, parent)
