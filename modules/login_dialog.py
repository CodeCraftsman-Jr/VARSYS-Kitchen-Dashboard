"""
Kitchen Dashboard - Login Dialog
This module provides a login dialog for Firebase authentication.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QMessageBox,
                              QFormLayout, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from datetime import datetime

# Import session manager for persistent login
try:
    from .session_manager import get_session_manager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False

# Import responsive dialog utilities
try:
    from .responsive_dialog_utils import ResponsiveDialog, get_responsive_dialog_manager
    RESPONSIVE_AVAILABLE = True
except ImportError:
    RESPONSIVE_AVAILABLE = False
    ResponsiveDialog = QDialog

class LoginDialog(ResponsiveDialog):
    """Subscription-based login dialog for Kitchen Dashboard v1.0.6"""

    # Signals emitted for authentication events
    login_successful = Signal(dict)
    login_failed = Signal(str)

    def __init__(self, parent=None, firebase_config_manager=None):
        # Initialize responsive dialog
        super().__init__(title="Kitchen Dashboard - Subscriber Login v1.0.6", parent=parent, modal=True)

        # Store Firebase configuration manager
        self.firebase_config_manager = firebase_config_manager

        # Set minimum size for desktop
        self.setMinimumSize(400, 300)

        # Set up the UI
        self.setup_ui()

        # Apply additional responsive styling
        self.apply_login_responsive_styling()

        # Check for existing session and auto-login if available
        self.check_existing_session()
        
    def setup_ui(self):
        """Set up the login UI"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Main layout without tabs since we're only keeping login
        login_layout = QVBoxLayout()
        
        # Header label
        header_label = QLabel("Kitchen Dashboard Login")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        login_layout.addWidget(header_label)
        
        # Login form
        login_form = QGroupBox("Login with Email")
        login_form_layout = QFormLayout(login_form)
        
        # Email field
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Enter your email")
        login_form_layout.addRow("Email:", self.login_email)
        
        # Password field
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        login_form_layout.addRow("Password:", self.login_password)

        # Remember Me checkbox
        self.remember_me_checkbox = QCheckBox("Remember me for 30 days")
        self.remember_me_checkbox.setStyleSheet("color: #2c3e50; margin: 8px 0;")
        login_form_layout.addRow("", self.remember_me_checkbox)

        # Add form to layout
        login_layout.addWidget(login_form)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: #2980b9; color: white; padding: 8px;")
        self.login_button.clicked.connect(self.login)
        login_layout.addWidget(self.login_button)
        
        # Note about Firebase setup
        note_label = QLabel("Note: You must have Firebase set up to use this application.")
        note_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        note_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(note_label)
        
        # Add login layout to main layout
        layout.addLayout(login_layout)

    def apply_login_responsive_styling(self):
        """Apply responsive styling specific to login dialog"""
        if not RESPONSIVE_AVAILABLE:
            # Fallback styling for non-responsive mode
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                    border-radius: 8px;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                }
                QLineEdit {
                    padding: 12px;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    font-size: 14px;
                    margin: 4px 0;
                }
                QLineEdit:focus {
                    border-color: #3b82f6;
                }
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 600;
                    margin: 8px 0;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
                QPushButton:pressed {
                    background-color: #1d4ed8;
                }
                QGroupBox {
                    font-weight: 600;
                    border: 1px solid #e5e7eb;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 8px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px 0 4px;
                    background-color: white;
                }
            """)
            return

        # Get responsive manager for device-specific styling
        try:
            from .responsive_design_manager import get_responsive_manager, DeviceType
            responsive_manager = get_responsive_manager()

            if responsive_manager:
                device_type = responsive_manager.current_device_type
                styles = responsive_manager.get_responsive_styles(device_type)

                # Device-specific styling
                if device_type == DeviceType.MOBILE:
                    # Mobile-specific login styling
                    additional_style = f"""
                        QLineEdit {{
                            min-height: 48px;
                            font-size: 16px;
                            padding: 16px;
                        }}
                        QPushButton {{
                            min-height: 52px;
                            font-size: 16px;
                            padding: 16px 24px;
                        }}
                        QLabel {{
                            font-size: 16px;
                            margin: 8px 0;
                        }}
                        QGroupBox {{
                            padding: 16px;
                            margin: 16px 0;
                        }}
                    """
                elif device_type == DeviceType.TABLET:
                    # Tablet-specific login styling
                    additional_style = f"""
                        QLineEdit {{
                            min-height: 44px;
                            font-size: 15px;
                            padding: 14px;
                        }}
                        QPushButton {{
                            min-height: 48px;
                            font-size: 15px;
                            padding: 14px 20px;
                        }}
                        QLabel {{
                            font-size: 15px;
                            margin: 6px 0;
                        }}
                        QGroupBox {{
                            padding: 14px;
                            margin: 12px 0;
                        }}
                    """
                else:
                    # Desktop styling
                    additional_style = f"""
                        QLineEdit {{
                            min-height: 40px;
                            font-size: 14px;
                            padding: 12px;
                        }}
                        QPushButton {{
                            min-height: 44px;
                            font-size: 14px;
                            padding: 12px 18px;
                        }}
                        QLabel {{
                            font-size: 14px;
                            margin: 4px 0;
                        }}
                        QGroupBox {{
                            padding: 12px;
                            margin: 8px 0;
                        }}
                    """

                # Combine with existing responsive styling
                current_style = self.styleSheet()
                self.setStyleSheet(current_style + additional_style)

        except ImportError:
            pass  # Fallback styling already applied above

    def check_existing_session(self):
        """Check for existing valid session and auto-login if available"""
        if not SESSION_MANAGER_AVAILABLE:
            return

        try:
            session_manager = get_session_manager()
            session_data = session_manager.load_session()

            if session_data and session_data.get('user_info'):
                user_info = session_data['user_info']
                print(f"[SESSION] Found valid session for user: {user_info.get('email', 'Unknown')}")

                # Update session activity
                session_manager.update_session_activity(user_info)

                # Auto-login with saved session
                self.login_successful.emit(user_info)
                self.accept()
                return True

        except Exception as e:
            print(f"[SESSION] Error checking existing session: {e}")

        return False

    @staticmethod
    def clear_saved_sessions(clear_remember_me=True):
        """Clear saved sessions (for logout functionality)"""
        if not SESSION_MANAGER_AVAILABLE:
            return False

        try:
            session_manager = get_session_manager()
            session_manager.clear_session(clear_remember_me=clear_remember_me)
            print(f"[SESSION] Cleared sessions (remember_me={clear_remember_me})")
            return True
        except Exception as e:
            print(f"[SESSION] Error clearing sessions: {e}")
            return False

    def login(self):
        """Handle login button click with enhanced Firebase configuration support"""
        email = self.login_email.text().strip()
        password = self.login_password.text()

        # Basic validation
        if not email or not password:
            QMessageBox.warning(
                self,
                "Login Error",
                "Please enter both email and password."
            )
            return

        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText("Authenticating...")

        try:
            # Check Firebase configuration
            if not self.firebase_config_manager or not self.firebase_config_manager.is_configured():
                error_msg = "Firebase is not configured. Please check your Firebase settings."
                self.show_configuration_error(error_msg)
                return

            # Check if Firebase authentication is available
            from modules import firebase_integration
            if not firebase_integration.PYREBASE_AVAILABLE:
                error_msg = "Firebase authentication is not available. Please install pyrebase4."
                self.show_authentication_error(error_msg)
                return

            # Initialize Firebase with configuration
            firebase_config = self.firebase_config_manager.get_firebase_config_dict()
            if not firebase_integration.initialize_firebase_with_config(firebase_config):
                error_msg = "Failed to initialize Firebase. Please check your configuration."
                self.show_authentication_error(error_msg)
                return

            # Attempt to sign in with subscriber credentials
            user = firebase_integration.sign_in_with_email(email, password)
            if user:
                # Add additional user information for subscriber
                user_info = {
                    **user,
                    'login_time': str(datetime.now()),
                    'session_id': f"session_{datetime.now().timestamp()}",
                    'app_version': '1.0.6',
                    'subscription_type': 'firebase_managed',
                    'email': email  # Ensure email is included for session management
                }

                # Save session if Remember Me is checked and session manager is available
                if SESSION_MANAGER_AVAILABLE and self.remember_me_checkbox.isChecked():
                    try:
                        session_manager = get_session_manager()
                        remember_me = self.remember_me_checkbox.isChecked()
                        if session_manager.save_session(user_info, remember_me=remember_me):
                            print(f"[SESSION] Session saved with remember_me={remember_me}")
                        else:
                            print("[SESSION] Failed to save session")
                    except Exception as e:
                        print(f"[SESSION] Error saving session: {e}")

                # Emit signal with user info
                self.login_successful.emit(user_info)
                self.accept()
            else:
                error_msg = "Invalid subscriber credentials. Only users created by the administrator can access this application."
                self.show_authentication_error(error_msg)

        except Exception as e:
            error_msg = f"An error occurred during login: {str(e)}"
            self.show_authentication_error(error_msg)

        finally:
            # Re-enable login button
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")

    def show_configuration_error(self, message):
        """Show configuration error - ONLINE-ONLY MODE"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Firebase Configuration Required")
        msg.setText("Kitchen Dashboard v1.0.6 requires Firebase configuration.")
        msg.setInformativeText(f"{message}\n\nThis application requires online authentication to function.")
        msg.setIcon(QMessageBox.Critical)

        configure_btn = msg.addButton("Configure Firebase", QMessageBox.ActionRole)
        exit_btn = msg.addButton("Exit Application", QMessageBox.RejectRole)

        msg.exec()

        if msg.clickedButton() == configure_btn:
            self.show_firebase_configuration()
        else:
            from PySide6.QtWidgets import QApplication
            QApplication.quit()

    def show_authentication_error(self, message):
        """Show authentication error for subscription-based access"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Subscriber Authentication Failed")
        msg.setText("Access Denied")
        msg.setInformativeText(
            f"{message}\n\n"
            "This is a subscription-based application. Only users with accounts "
            "created by the administrator can access the Kitchen Dashboard.\n\n"
            "If you believe you should have access, please contact the administrator."
        )
        msg.setIcon(QMessageBox.Warning)
        msg.exec()
        self.login_failed.emit(message)

    def show_firebase_configuration(self):
        """Show Firebase configuration dialog"""
        try:
            from .firebase_config_widget import FirebaseConfigWidget
            config_dialog = QDialog(self)
            config_dialog.setWindowTitle("Firebase Configuration")
            config_dialog.setModal(True)
            config_dialog.resize(500, 400)

            layout = QVBoxLayout(config_dialog)
            config_widget = FirebaseConfigWidget(self.firebase_config_manager)
            layout.addWidget(config_widget)

            # Add buttons
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Save & Continue")
            cancel_btn = QPushButton("Cancel")

            save_btn.clicked.connect(lambda: self.save_config_and_continue(config_dialog, config_widget))
            cancel_btn.clicked.connect(config_dialog.reject)

            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)

            config_dialog.exec()

        except ImportError:
            QMessageBox.information(
                self,
                "Configuration",
                "Please manually configure Firebase by editing the firebase_config.json file."
            )

    def save_config_and_continue(self, dialog, config_widget):
        """Save Firebase configuration and continue with login"""
        if config_widget.save_configuration():
            dialog.accept()
            # Reload configuration
            if self.firebase_config_manager:
                self.firebase_config_manager.load_configuration()
        else:
            QMessageBox.warning(dialog, "Save Error", "Failed to save configuration. Please try again.")
    
    # Signup functionality removed as requested
    
    def reject(self):
        """Override reject to exit application - ONLINE-ONLY MODE"""
        # ONLINE-ONLY: Exit the application when login dialog is closed/canceled
        # No offline mode is permitted
        from PySide6.QtWidgets import QApplication, QMessageBox

        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Exit Application")
        msg.setText("Kitchen Dashboard v1.0.6 requires online authentication.")
        msg.setInformativeText("Are you sure you want to exit the application?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec() == QMessageBox.Yes:
            QApplication.quit()
        # If No, do nothing - keep the login dialog open
