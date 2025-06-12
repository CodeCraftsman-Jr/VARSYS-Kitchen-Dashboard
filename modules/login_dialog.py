"""
Kitchen Dashboard - Login Dialog
This module provides a login dialog for Firebase authentication.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QMessageBox, QTabWidget,
                              QWidget, QFormLayout, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QGuiApplication

# Import responsive dialog utilities
try:
    from .responsive_dialog_utils import ResponsiveDialog, get_responsive_dialog_manager
    RESPONSIVE_AVAILABLE = True
except ImportError:
    RESPONSIVE_AVAILABLE = False
    ResponsiveDialog = QDialog

class LoginDialog(ResponsiveDialog):
    """Responsive login dialog for Firebase authentication"""

    # Signal emitted when login is successful
    login_successful = Signal(dict)

    def __init__(self, parent=None):
        # Initialize responsive dialog
        super().__init__("Kitchen Dashboard - Login", parent, modal=True)

        # Set minimum size for desktop
        self.setMinimumSize(400, 300)

        # Set up the UI
        self.setup_ui()

        # Apply additional responsive styling
        self.apply_login_responsive_styling()
        
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

    def login(self):
        """Handle login button click"""
        email = self.login_email.text()
        password = self.login_password.text()
        
        # Basic validation
        if not email or not password:
            QMessageBox.warning(
                self,
                "Login Error",
                "Please enter both email and password."
            )
            return
        
        # Check if Firebase authentication is available
        try:
            from modules import firebase_integration
            if not firebase_integration.PYREBASE_AVAILABLE:
                QMessageBox.warning(
                    self,
                    "Authentication Error",
                    "Firebase authentication is not available. Please install pyrebase4."
                )
                return
                
            # Initialize Firebase
            if not firebase_integration.initialize_firebase():
                QMessageBox.warning(
                    self,
                    "Firebase Error",
                    "Failed to initialize Firebase. Please check your credentials."
                )
                return
                
            # Attempt to sign in
            user = firebase_integration.sign_in_with_email(email, password)
            if user:
                # Emit signal with user info
                self.login_successful.emit(user)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Login Failed",
                    "Invalid email or password. Please try again."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Login Error",
                f"An error occurred during login: {str(e)}"
            )
    
    # Signup functionality removed as requested
    
    def reject(self):
        """Override reject to exit application when dialog is closed"""
        # Exit the application when the login dialog is closed/canceled
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
        super().reject()
