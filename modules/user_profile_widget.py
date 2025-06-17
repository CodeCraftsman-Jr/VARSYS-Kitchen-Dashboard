"""
User Profile Widget for Kitchen Dashboard
Provides user information display and logout functionality
"""

from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QLabel, QDialog, QMessageBox, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush
from datetime import datetime
import logging

class UserProfileWidget(QWidget):
    """User profile widget with logout functionality"""
    
    # Signals
    logout_requested = Signal()
    profile_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.current_user = None
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setFixedSize(45, 35)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # User profile button
        self.profile_button = QPushButton()
        self.profile_button.setFixedSize(45, 35)
        self.profile_button.setText("👤")
        self.profile_button.setFont(QFont("Segoe UI", 16))
        self.profile_button.setToolTip("User Profile - Click for options")
        self.profile_button.clicked.connect(self.show_profile_menu)
        
        layout.addWidget(self.profile_button)
        
    def apply_styling(self):
        """Apply modern styling to the widget"""
        self.profile_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        
    def set_user_info(self, user_info):
        """Set current user information"""
        self.current_user = user_info
        
        if user_info:
            email = user_info.get('email', 'Unknown User')
            display_name = user_info.get('displayName', email.split('@')[0])
            
            # Update tooltip with user info
            tooltip_text = f"Logged in as: {display_name}\nEmail: {email}\nClick for profile options"
            self.profile_button.setToolTip(tooltip_text)
            
            # Update button text to show first letter of name
            if display_name:
                self.profile_button.setText(display_name[0].upper())
            else:
                self.profile_button.setText("👤")
                
            self.logger.info(f"User profile updated for: {email}")
        else:
            self.profile_button.setText("👤")
            self.profile_button.setToolTip("No user logged in")
            
    def show_profile_menu(self):
        """Show user profile menu with options"""
        if not self.current_user:
            QMessageBox.warning(self, "No User", "No user is currently logged in.")
            return

        # Create profile dialog
        dialog = UserProfileDialog(self.current_user, self)
        dialog.logout_requested.connect(self.handle_logout_request)
        dialog.account_settings_requested.connect(self.handle_account_settings_request)
        dialog.exec()

    def handle_account_settings_request(self):
        """Handle account settings request"""
        try:
            from modules.account_settings_dialog import AccountSettingsDialog

            settings_dialog = AccountSettingsDialog(self.current_user, self)
            settings_dialog.profile_updated.connect(self.handle_profile_updated)
            settings_dialog.settings_changed.connect(self.handle_settings_changed)
            settings_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error opening account settings: {e}")
            QMessageBox.warning(self, "Error", f"Could not open account settings: {str(e)}")

    def handle_profile_updated(self, updated_user_info):
        """Handle profile update"""
        self.current_user = updated_user_info
        self.set_user_info(updated_user_info)
        self.logger.info("User profile updated successfully")

    def handle_settings_changed(self, settings):
        """Handle settings change"""
        self.logger.info("User settings updated successfully")
        
    def handle_logout_request(self):
        """Handle logout request from profile dialog"""
        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Logout")
        msg.setText("Are you sure you want to logout?")
        msg.setInformativeText("You will need to login again to access the application.")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            self.logger.info("User confirmed logout")
            self.logout_requested.emit()


class UserProfileDialog(QDialog):
    """User profile information dialog"""

    logout_requested = Signal()
    account_settings_requested = Signal()

    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("User Profile")
        self.setModal(True)
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("User Profile")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # User info frame
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(8)
        
        # User details
        email = self.user_info.get('email', 'Unknown')
        display_name = self.user_info.get('displayName', email.split('@')[0])
        user_id = self.user_info.get('localId', self.user_info.get('uid', 'Unknown'))
        login_time = self.user_info.get('login_time', 'Unknown')
        
        # Display name
        name_label = QLabel(f"Name: {display_name}")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        info_layout.addWidget(name_label)
        
        # Email
        email_label = QLabel(f"Email: {email}")
        email_label.setFont(QFont("Segoe UI", 10))
        info_layout.addWidget(email_label)
        
        # User ID
        uid_label = QLabel(f"User ID: {user_id[:8]}...")  # Show first 8 chars
        uid_label.setFont(QFont("Segoe UI", 9))
        uid_label.setStyleSheet("color: #666;")
        info_layout.addWidget(uid_label)
        
        # Login time
        if login_time != 'Unknown':
            try:
                login_dt = datetime.fromisoformat(login_time.replace('Z', '+00:00'))
                login_str = login_dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                login_str = login_time
        else:
            login_str = "Unknown"
            
        login_label = QLabel(f"Login Time: {login_str}")
        login_label.setFont(QFont("Segoe UI", 9))
        login_label.setStyleSheet("color: #666;")
        info_layout.addWidget(login_label)
        
        layout.addWidget(info_frame)
        
        # Buttons
        button_layout = QHBoxLayout()

        # Account settings button
        settings_button = QPushButton("Account Settings")
        settings_button.clicked.connect(self.handle_account_settings)
        button_layout.addWidget(settings_button)

        # Session management button
        session_button = QPushButton("Manage Sessions")
        session_button.clicked.connect(self.show_session_management)
        button_layout.addWidget(session_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.handle_logout)
        button_layout.addWidget(logout_button)

        layout.addLayout(button_layout)
        
    def apply_styling(self):
        """Apply styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QLabel {
                color: #374151;
            }
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#logout {
                background-color: #ef4444;
            }
            QPushButton#logout:hover {
                background-color: #dc2626;
            }
            QPushButton#logout:pressed {
                background-color: #b91c1c;
            }
        """)
        
        # Apply special styling to logout button
        logout_buttons = self.findChildren(QPushButton)
        for button in logout_buttons:
            if button.text() == "Logout":
                button.setObjectName("logout")
                
    def show_session_management(self):
        """Show session management dialog"""
        try:
            # Try to get the main application window
            main_window = None

            # First try parent_app
            if hasattr(self, 'parent_app') and self.parent_app:
                main_window = self.parent_app
            # Then try parent()
            elif self.parent():
                main_window = self.parent()
                # If parent is not the main window, try to find it
                while main_window and not hasattr(main_window, 'show_session_management_dialog'):
                    main_window = main_window.parent()

            # If we found the main window and it has the method, call it
            if main_window and hasattr(main_window, 'show_session_management_dialog'):
                main_window.show_session_management_dialog()
            else:
                # Fallback: show our own session management dialog
                self.show_builtin_session_management()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show session management: {e}")

    def show_builtin_session_management(self):
        """Show built-in session management dialog"""
        try:
            from .session_manager import get_session_manager
            session_manager = get_session_manager()

            session_info = session_manager.get_session_info()

            dialog = QDialog(self)
            dialog.setWindowTitle("Session Management")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # Session info
            info_label = QLabel("Saved Session Information:")
            info_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            layout.addWidget(info_label)

            # Current session
            if session_info.get('has_current_session'):
                current_time = session_info.get('current_session_time', 'Unknown')
                current_label = QLabel(f"• Current session: {current_time}")
                layout.addWidget(current_label)

            # Remember me session
            if session_info.get('has_remember_me_session'):
                remember_time = session_info.get('remember_me_session_time', 'Unknown')
                remember_label = QLabel(f"• Remember me session: {remember_time}")
                layout.addWidget(remember_label)

            if not session_info.get('has_current_session') and not session_info.get('has_remember_me_session'):
                no_session_label = QLabel("No saved sessions found.")
                layout.addWidget(no_session_label)

            # Buttons
            button_layout = QHBoxLayout()

            clear_current_btn = QPushButton("Clear Current Session")
            clear_current_btn.clicked.connect(lambda: self.clear_current_session_builtin(dialog, session_manager))
            button_layout.addWidget(clear_current_btn)

            clear_all_btn = QPushButton("Clear All Sessions")
            clear_all_btn.clicked.connect(lambda: self.clear_all_sessions_builtin(dialog, session_manager))
            button_layout.addWidget(clear_all_btn)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show session management: {e}")

    def clear_current_session_builtin(self, dialog, session_manager):
        """Clear current session using built-in dialog"""
        try:
            session_manager.clear_session(clear_remember_me=False)
            QMessageBox.information(dialog, "Success", "Current session cleared.")
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Failed to clear session: {e}")

    def clear_all_sessions_builtin(self, dialog, session_manager):
        """Clear all sessions using built-in dialog"""
        try:
            session_manager.clear_session(clear_remember_me=True)
            QMessageBox.information(dialog, "Success", "All sessions cleared.")
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Failed to clear sessions: {e}")

    def handle_account_settings(self):
        """Handle account settings request"""
        self.account_settings_requested.emit()
        self.accept()  # Close the profile dialog

    def handle_logout(self):
        """Handle logout button click"""
        self.logout_requested.emit()
        self.accept()
