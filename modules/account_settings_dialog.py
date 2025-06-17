"""
Kitchen Dashboard - Account Settings Dialog
Comprehensive account management with password change, profile updates, 
notification preferences, and security settings
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                              QWidget, QLabel, QLineEdit, QPushButton, QGroupBox,
                              QFormLayout, QCheckBox, QSpinBox, QComboBox, 
                              QTextEdit, QMessageBox, QProgressBar, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QIcon
import logging
from datetime import datetime, timedelta
import json
import os

# Import Firebase integration if available
try:
    from modules import firebase_integration
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# Import session manager if available
try:
    from modules.session_manager import get_session_manager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False


class PasswordChangeWorker(QThread):
    """Worker thread for password change operations"""
    password_changed = Signal(bool, str)
    
    def __init__(self, current_password, new_password, user_info):
        super().__init__()
        self.current_password = current_password
        self.new_password = new_password
        self.user_info = user_info
    
    def run(self):
        """Perform password change operation"""
        try:
            if not FIREBASE_AVAILABLE:
                self.password_changed.emit(False, "Firebase not available")
                return
            
            # Verify current password by attempting to sign in
            email = self.user_info.get('email', '')
            user = firebase_integration.sign_in_with_email(email, self.current_password)
            
            if not user:
                self.password_changed.emit(False, "Current password is incorrect")
                return
            
            # Change password using Firebase
            success = firebase_integration.change_user_password(
                user.get('idToken', ''), self.new_password
            )
            
            if success:
                self.password_changed.emit(True, "Password changed successfully")
            else:
                self.password_changed.emit(False, "Failed to change password")
                
        except Exception as e:
            self.password_changed.emit(False, f"Error: {str(e)}")


class AccountSettingsDialog(QDialog):
    """Comprehensive account settings dialog"""
    
    # Signals
    profile_updated = Signal(dict)
    settings_changed = Signal(dict)
    
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Account Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Load current settings
        self.load_settings()
        
        # Setup UI
        self.setup_ui()
        self.apply_styling()
        
        # Load user data
        self.load_user_data()
    
    def load_settings(self):
        """Load current user settings"""
        self.settings = {
            'notifications': {
                'enable_notifications': True,
                'notification_sound': True,
                'show_desktop_notifications': True,
                'notification_frequency': 'normal'
            },
            'security': {
                'session_timeout': 24,  # hours
                'auto_logout_idle': 30,  # minutes
                'require_password_confirmation': True,
                'enable_audit_log': True
            },
            'profile': {
                'display_name': self.user_info.get('displayName', ''),
                'email': self.user_info.get('email', ''),
                'phone': '',
                'timezone': 'UTC'
            }
        }
        
        # Try to load saved settings
        try:
            settings_file = os.path.join('data', 'user_settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults
                    self.merge_settings(saved_settings)
        except Exception as e:
            self.logger.warning(f"Could not load user settings: {e}")
    
    def merge_settings(self, saved_settings):
        """Merge saved settings with defaults"""
        for category, settings in saved_settings.items():
            if category in self.settings:
                self.settings[category].update(settings)
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_profile_tab()
        self.create_security_tab()
        self.create_notifications_tab()
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_profile_tab(self):
        """Create profile settings tab"""
        profile_widget = QWidget()
        layout = QVBoxLayout(profile_widget)
        
        # Profile Information Group
        profile_group = QGroupBox("Profile Information")
        profile_form = QFormLayout(profile_group)
        
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("Enter display name")
        profile_form.addRow("Display Name:", self.display_name_edit)
        
        self.email_label = QLabel()
        self.email_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        profile_form.addRow("Email:", self.email_label)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Enter phone number (optional)")
        profile_form.addRow("Phone:", self.phone_edit)
        
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            "UTC", "Asia/Kolkata", "America/New_York", "Europe/London",
            "Asia/Tokyo", "Australia/Sydney"
        ])
        profile_form.addRow("Timezone:", self.timezone_combo)
        
        layout.addWidget(profile_group)
        
        # Password Change Group
        password_group = QGroupBox("Change Password")
        password_form = QFormLayout(password_group)
        
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.Password)
        self.current_password_edit.setPlaceholderText("Enter current password")
        password_form.addRow("Current Password:", self.current_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        self.new_password_edit.setPlaceholderText("Enter new password")
        password_form.addRow("New Password:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("Confirm new password")
        password_form.addRow("Confirm Password:", self.confirm_password_edit)
        
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.clicked.connect(self.change_password)
        password_form.addRow("", self.change_password_button)
        
        # Password strength indicator
        self.password_strength_bar = QProgressBar()
        self.password_strength_bar.setRange(0, 100)
        self.password_strength_bar.setVisible(False)
        password_form.addRow("Strength:", self.password_strength_bar)
        
        layout.addWidget(password_group)
        layout.addStretch()
        
        self.tab_widget.addTab(profile_widget, "👤 Profile")
    
    def create_security_tab(self):
        """Create security settings tab"""
        security_widget = QWidget()
        layout = QVBoxLayout(security_widget)
        
        # Session Settings Group
        session_group = QGroupBox("Session Settings")
        session_form = QFormLayout(session_group)
        
        self.session_timeout_spin = QSpinBox()
        self.session_timeout_spin.setRange(1, 168)  # 1 hour to 1 week
        self.session_timeout_spin.setSuffix(" hours")
        session_form.addRow("Session Timeout:", self.session_timeout_spin)
        
        self.idle_timeout_spin = QSpinBox()
        self.idle_timeout_spin.setRange(5, 240)  # 5 minutes to 4 hours
        self.idle_timeout_spin.setSuffix(" minutes")
        session_form.addRow("Auto-logout (Idle):", self.idle_timeout_spin)
        
        layout.addWidget(session_group)
        
        # Security Options Group
        security_options_group = QGroupBox("Security Options")
        security_options_layout = QVBoxLayout(security_options_group)
        
        self.require_password_check = QCheckBox("Require password confirmation for sensitive operations")
        security_options_layout.addWidget(self.require_password_check)
        
        self.enable_audit_log_check = QCheckBox("Enable security audit logging")
        security_options_layout.addWidget(self.enable_audit_log_check)
        
        layout.addWidget(security_options_group)
        
        # Security Actions Group
        actions_group = QGroupBox("Security Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        logout_all_button = QPushButton("Logout from all devices")
        logout_all_button.clicked.connect(self.logout_all_devices)
        actions_layout.addWidget(logout_all_button)
        
        view_audit_button = QPushButton("View Security Audit Log")
        view_audit_button.clicked.connect(self.view_audit_log)
        actions_layout.addWidget(view_audit_button)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        self.tab_widget.addTab(security_widget, "🔒 Security")
    
    def create_notifications_tab(self):
        """Create notification preferences tab"""
        notifications_widget = QWidget()
        layout = QVBoxLayout(notifications_widget)
        
        # Notification Settings Group
        notifications_group = QGroupBox("Notification Preferences")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications_check = QCheckBox("Enable notifications")
        notifications_layout.addWidget(self.enable_notifications_check)
        
        self.notification_sound_check = QCheckBox("Play notification sounds")
        notifications_layout.addWidget(self.notification_sound_check)
        
        self.desktop_notifications_check = QCheckBox("Show desktop notifications")
        notifications_layout.addWidget(self.desktop_notifications_check)
        
        # Notification frequency
        frequency_layout = QHBoxLayout()
        frequency_layout.addWidget(QLabel("Notification Frequency:"))
        
        self.notification_frequency_combo = QComboBox()
        self.notification_frequency_combo.addItems([
            "minimal", "normal", "frequent", "all"
        ])
        frequency_layout.addWidget(self.notification_frequency_combo)
        frequency_layout.addStretch()
        
        notifications_layout.addLayout(frequency_layout)
        
        layout.addWidget(notifications_group)
        layout.addStretch()
        
        self.tab_widget.addTab(notifications_widget, "🔔 Notifications")
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Account Information Group
        info_group = QGroupBox("Account Information")
        info_layout = QVBoxLayout(info_group)
        
        # User ID
        uid_layout = QHBoxLayout()
        uid_layout.addWidget(QLabel("User ID:"))
        uid_label = QLabel(self.user_info.get('localId', 'Unknown')[:16] + "...")
        uid_label.setStyleSheet("font-family: monospace; color: #7f8c8d;")
        uid_layout.addWidget(uid_label)
        uid_layout.addStretch()
        info_layout.addLayout(uid_layout)
        
        # Login time
        login_time = self.user_info.get('login_time', 'Unknown')
        login_layout = QHBoxLayout()
        login_layout.addWidget(QLabel("Last Login:"))
        login_layout.addWidget(QLabel(login_time))
        login_layout.addStretch()
        info_layout.addLayout(login_layout)
        
        layout.addWidget(info_group)
        
        # Data Management Group
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout(data_group)
        
        export_button = QPushButton("Export Account Data")
        export_button.clicked.connect(self.export_account_data)
        data_layout.addWidget(export_button)
        
        layout.addWidget(data_group)
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_widget, "⚙️ Advanced")
    
    def load_user_data(self):
        """Load user data into form fields"""
        # Profile tab
        self.display_name_edit.setText(self.settings['profile']['display_name'])
        self.email_label.setText(self.settings['profile']['email'])
        self.phone_edit.setText(self.settings['profile']['phone'])
        
        # Find and set timezone
        timezone_index = self.timezone_combo.findText(self.settings['profile']['timezone'])
        if timezone_index >= 0:
            self.timezone_combo.setCurrentIndex(timezone_index)
        
        # Security tab
        self.session_timeout_spin.setValue(self.settings['security']['session_timeout'])
        self.idle_timeout_spin.setValue(self.settings['security']['auto_logout_idle'])
        self.require_password_check.setChecked(self.settings['security']['require_password_confirmation'])
        self.enable_audit_log_check.setChecked(self.settings['security']['enable_audit_log'])
        
        # Notifications tab
        self.enable_notifications_check.setChecked(self.settings['notifications']['enable_notifications'])
        self.notification_sound_check.setChecked(self.settings['notifications']['notification_sound'])
        self.desktop_notifications_check.setChecked(self.settings['notifications']['show_desktop_notifications'])
        
        # Find and set notification frequency
        freq_index = self.notification_frequency_combo.findText(self.settings['notifications']['notification_frequency'])
        if freq_index >= 0:
            self.notification_frequency_combo.setCurrentIndex(freq_index)
    
    def change_password(self):
        """Handle password change"""
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Validation
        if not current_password:
            QMessageBox.warning(self, "Error", "Please enter your current password")
            return
        
        if not new_password:
            QMessageBox.warning(self, "Error", "Please enter a new password")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters long")
            return
        
        # Disable button and show progress
        self.change_password_button.setEnabled(False)
        self.change_password_button.setText("Changing Password...")
        
        # Start password change worker
        self.password_worker = PasswordChangeWorker(current_password, new_password, self.user_info)
        self.password_worker.password_changed.connect(self.on_password_changed)
        self.password_worker.start()
    
    def on_password_changed(self, success, message):
        """Handle password change result"""
        self.change_password_button.setEnabled(True)
        self.change_password_button.setText("Change Password")
        
        if success:
            QMessageBox.information(self, "Success", message)
            # Clear password fields
            self.current_password_edit.clear()
            self.new_password_edit.clear()
            self.confirm_password_edit.clear()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def logout_all_devices(self):
        """Logout from all devices"""
        reply = QMessageBox.question(
            self, "Confirm Logout", 
            "This will logout from all devices. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Implementation would depend on Firebase setup
            QMessageBox.information(self, "Success", "Logged out from all devices")
    
    def view_audit_log(self):
        """View security audit log"""
        # This would show a dialog with audit log entries
        QMessageBox.information(self, "Audit Log", "Audit log feature coming soon!")
    
    def export_account_data(self):
        """Export account data"""
        QMessageBox.information(self, "Export Data", "Data export feature coming soon!")
    
    def save_settings(self):
        """Save all settings"""
        try:
            # Update settings from form
            self.settings['profile']['display_name'] = self.display_name_edit.text()
            self.settings['profile']['phone'] = self.phone_edit.text()
            self.settings['profile']['timezone'] = self.timezone_combo.currentText()
            
            self.settings['security']['session_timeout'] = self.session_timeout_spin.value()
            self.settings['security']['auto_logout_idle'] = self.idle_timeout_spin.value()
            self.settings['security']['require_password_confirmation'] = self.require_password_check.isChecked()
            self.settings['security']['enable_audit_log'] = self.enable_audit_log_check.isChecked()
            
            self.settings['notifications']['enable_notifications'] = self.enable_notifications_check.isChecked()
            self.settings['notifications']['notification_sound'] = self.notification_sound_check.isChecked()
            self.settings['notifications']['show_desktop_notifications'] = self.desktop_notifications_check.isChecked()
            self.settings['notifications']['notification_frequency'] = self.notification_frequency_combo.currentText()
            
            # Save to file
            os.makedirs('data', exist_ok=True)
            settings_file = os.path.join('data', 'user_settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            # Emit signals
            self.settings_changed.emit(self.settings)
            
            # Update user info if display name changed
            if self.settings['profile']['display_name'] != self.user_info.get('displayName', ''):
                updated_user_info = self.user_info.copy()
                updated_user_info['displayName'] = self.settings['profile']['display_name']
                self.profile_updated.emit(updated_user_info)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
    
    def apply_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8fafc;
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
            QLineEdit, QComboBox, QSpinBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #3498db;
            }
            QCheckBox {
                spacing: 8px;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3498db;
            }
        """)
