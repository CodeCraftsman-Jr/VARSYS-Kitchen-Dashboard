"""
Enhanced Authentication Widget
Modern authentication interface with improved user experience
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QProgressBar,
                             QMessageBox, QCheckBox, QTabWidget, QFormLayout,
                             QGroupBox, QTextEdit, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPalette

# Import optimized Firebase manager
try:
    from .optimized_firebase_manager import get_optimized_firebase_manager
    from .activity_tracker import track_user_action, track_system_event
except ImportError:
    get_optimized_firebase_manager = None
    def track_user_action(*args, **kwargs): pass
    def track_system_event(*args, **kwargs): pass

class AuthenticationWorker(QThread):
    """Background authentication worker"""
    
    authentication_completed = Signal(bool, str)  # success, message
    
    def __init__(self, email: str, password: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.password = password
        self.firebase_manager = get_optimized_firebase_manager() if get_optimized_firebase_manager else None
    
    def run(self):
        """Perform authentication in background"""
        try:
            if not self.firebase_manager:
                self.authentication_completed.emit(False, "Firebase not available")
                return
            
            success = self.firebase_manager.authenticate_user(self.email, self.password)
            
            if success:
                self.authentication_completed.emit(True, "Authentication successful")
            else:
                self.authentication_completed.emit(False, "Authentication failed")
                
        except Exception as e:
            self.authentication_completed.emit(False, f"Authentication error: {str(e)}")

class EnhancedAuthWidget(QWidget):
    """
    Enhanced authentication widget with:
    - Modern UI design
    - Background authentication
    - Session management
    - Usage statistics
    - Error handling
    """
    
    # Signals
    authentication_changed = Signal(bool, dict)  # authenticated, user_info
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Get Firebase manager
        self.firebase_manager = get_optimized_firebase_manager() if get_optimized_firebase_manager else None
        
        # Authentication state
        self.is_authenticated = False
        self.current_user = None
        
        # Initialize UI
        self.init_ui()
        
        # Connect Firebase manager signals
        if self.firebase_manager:
            self.firebase_manager.authentication_changed.connect(self.on_authentication_changed)
            self.firebase_manager.error_occurred.connect(self.on_firebase_error)
        
        # Setup status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)  # Update every 30 seconds
        
        self.logger.info("Enhanced Authentication Widget initialized")
        track_system_event("auth_widget", "initialized", "Enhanced authentication widget started")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create tabs for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #0f172a;
            }
        """)
        
        # Authentication tab
        self.create_auth_tab()
        
        # Status tab
        self.create_status_tab()
        
        layout.addWidget(self.tabs)
    
    def create_auth_tab(self):
        """Create authentication tab"""
        auth_widget = QWidget()
        layout = QVBoxLayout(auth_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Firebase Authentication")
        header_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Status indicator
        self.auth_status_frame = QFrame()
        self.auth_status_frame.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        status_layout = QHBoxLayout(self.auth_status_frame)
        self.auth_status_label = QLabel("🔒 Not authenticated")
        self.auth_status_label.setStyleSheet("color: #92400e; font-weight: 500;")
        status_layout.addWidget(self.auth_status_label)
        
        layout.addWidget(self.auth_status_frame)
        
        # Authentication form
        self.create_auth_form(layout)
        
        # User info section (hidden initially)
        self.create_user_info_section(layout)
        
        layout.addStretch()
        
        self.tabs.addTab(auth_widget, "Authentication")
    
    def create_auth_form(self, parent_layout):
        """Create authentication form"""
        form_group = QGroupBox("Sign In")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(16)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        form_layout.addRow("Email:", self.email_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        form_layout.addRow("Password:", self.password_input)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet("color: #64748b; font-size: 12px;")
        form_layout.addRow("", self.remember_checkbox)
        
        # Sign in button
        self.signin_button = QPushButton("Sign In")
        self.signin_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.signin_button.clicked.connect(self.sign_in)
        form_layout.addRow("", self.signin_button)
        
        # Progress bar (hidden initially)
        self.auth_progress = QProgressBar()
        self.auth_progress.setVisible(False)
        self.auth_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        form_layout.addRow("", self.auth_progress)
        
        parent_layout.addWidget(form_group)
    
    def create_user_info_section(self, parent_layout):
        """Create user information section"""
        self.user_info_group = QGroupBox("User Information")
        self.user_info_group.setVisible(False)
        
        info_layout = QVBoxLayout(self.user_info_group)
        info_layout.setSpacing(12)
        
        # User details
        self.user_details_label = QLabel()
        self.user_details_label.setStyleSheet("color: #374151; font-size: 14px; line-height: 1.5;")
        info_layout.addWidget(self.user_details_label)
        
        # Session info
        self.session_info_label = QLabel()
        self.session_info_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        info_layout.addWidget(self.session_info_label)
        
        # Sign out button
        self.signout_button = QPushButton("Sign Out")
        self.signout_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.signout_button.clicked.connect(self.sign_out)
        info_layout.addWidget(self.signout_button)
        
        parent_layout.addWidget(self.user_info_group)
    
    def create_status_tab(self):
        """Create status and usage tab"""
        status_widget = QWidget()
        layout = QVBoxLayout(status_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Firebase Status & Usage")
        header_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #0f172a;")
        layout.addWidget(header_label)
        
        # Connection status
        connection_group = QGroupBox("Connection Status")
        connection_layout = QVBoxLayout(connection_group)
        
        self.connection_status_label = QLabel("🔄 Checking connection...")
        self.connection_status_label.setStyleSheet("color: #6b7280; font-size: 14px; padding: 8px;")
        connection_layout.addWidget(self.connection_status_label)
        
        layout.addWidget(connection_group)
        
        # Usage statistics
        usage_group = QGroupBox("Daily Usage Statistics")
        usage_layout = QFormLayout(usage_group)
        
        self.reads_label = QLabel("0 / 50,000")
        self.reads_label.setStyleSheet("color: #374151; font-weight: 500;")
        usage_layout.addRow("Reads:", self.reads_label)
        
        self.writes_label = QLabel("0 / 20,000")
        self.writes_label.setStyleSheet("color: #374151; font-weight: 500;")
        usage_layout.addRow("Writes:", self.writes_label)
        
        self.reads_progress = QProgressBar()
        self.reads_progress.setMaximum(50000)
        self.reads_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 3px;
            }
        """)
        usage_layout.addRow("Read Usage:", self.reads_progress)
        
        self.writes_progress = QProgressBar()
        self.writes_progress.setMaximum(20000)
        self.writes_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #f59e0b;
                border-radius: 3px;
            }
        """)
        usage_layout.addRow("Write Usage:", self.writes_progress)
        
        layout.addWidget(usage_group)
        
        # Sync status
        sync_group = QGroupBox("Sync Operations")
        sync_layout = QVBoxLayout(sync_group)
        
        self.sync_status_text = QTextEdit()
        self.sync_status_text.setMaximumHeight(150)
        self.sync_status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #374151;
            }
        """)
        self.sync_status_text.setPlainText("No sync operations yet...")
        sync_layout.addWidget(self.sync_status_text)
        
        layout.addWidget(sync_group)
        
        layout.addStretch()
        
        self.tabs.addTab(status_widget, "Status")
    
    def sign_in(self):
        """Handle sign in"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return
        
        # Disable UI during authentication
        self.signin_button.setEnabled(False)
        self.auth_progress.setVisible(True)
        self.auth_progress.setRange(0, 0)  # Indeterminate progress
        
        track_user_action("auth_widget", "signin_attempt", f"Sign in attempt for {email}")
        
        # Start background authentication
        self.auth_worker = AuthenticationWorker(email, password)
        self.auth_worker.authentication_completed.connect(self.on_authentication_completed)
        self.auth_worker.start()
    
    def sign_out(self):
        """Handle sign out"""
        if self.firebase_manager:
            self.firebase_manager.sign_out()
        
        track_user_action("auth_widget", "signout", "User signed out")
    
    def on_authentication_completed(self, success: bool, message: str):
        """Handle authentication completion"""
        # Re-enable UI
        self.signin_button.setEnabled(True)
        self.auth_progress.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Authentication", "Successfully signed in!")
        else:
            QMessageBox.warning(self, "Authentication Failed", message)
            
        # Clear password field
        self.password_input.clear()
    
    def on_authentication_changed(self, authenticated: bool, user_info: Dict):
        """Handle authentication state change"""
        self.is_authenticated = authenticated
        self.current_user = user_info if authenticated else None
        
        if authenticated:
            # Update status
            self.auth_status_label.setText("🔓 Authenticated")
            self.auth_status_frame.setStyleSheet("""
                QFrame {
                    background-color: #d1fae5;
                    border: 1px solid #10b981;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            self.auth_status_label.setStyleSheet("color: #065f46; font-weight: 500;")
            
            # Show user info
            self.user_details_label.setText(f"""
                <b>Email:</b> {user_info.get('email', 'Unknown')}<br>
                <b>Display Name:</b> {user_info.get('display_name', 'Unknown')}<br>
                <b>User ID:</b> {user_info.get('user_id', 'Unknown')[:10]}...
            """)
            
            self.session_info_label.setText(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            self.user_info_group.setVisible(True)
            
            # Hide auth form
            self.email_input.clear()
            self.password_input.clear()
            
        else:
            # Update status
            self.auth_status_label.setText("🔒 Not authenticated")
            self.auth_status_frame.setStyleSheet("""
                QFrame {
                    background-color: #fef3c7;
                    border: 1px solid #f59e0b;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            self.auth_status_label.setStyleSheet("color: #92400e; font-weight: 500;")
            
            # Hide user info
            self.user_info_group.setVisible(False)
        
        # Emit signal for parent widgets
        self.authentication_changed.emit(authenticated, user_info)
    
    def on_firebase_error(self, operation: str, error_message: str):
        """Handle Firebase errors"""
        self.sync_status_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR in {operation}: {error_message}")
    
    def update_status(self):
        """Update status information"""
        if not self.firebase_manager:
            self.connection_status_label.setText("❌ Firebase not available")
            return
        
        # Update connection status
        if self.firebase_manager.is_authenticated():
            self.connection_status_label.setText("✅ Connected and authenticated")
        else:
            self.connection_status_label.setText("🔶 Connected but not authenticated")
        
        # Update usage statistics
        usage_stats = self.firebase_manager.get_daily_usage_stats()
        
        self.reads_label.setText(f"{usage_stats['reads']:,} / {usage_stats['max_reads']:,}")
        self.writes_label.setText(f"{usage_stats['writes']:,} / {usage_stats['max_writes']:,}")
        
        self.reads_progress.setValue(usage_stats['reads'])
        self.writes_progress.setValue(usage_stats['writes'])
        
        # Update progress bar colors based on usage
        if usage_stats['reads'] > usage_stats['max_reads'] * 0.8:
            self.reads_progress.setStyleSheet("""
                QProgressBar::chunk { background-color: #ef4444; }
            """)
        elif usage_stats['reads'] > usage_stats['max_reads'] * 0.6:
            self.reads_progress.setStyleSheet("""
                QProgressBar::chunk { background-color: #f59e0b; }
            """)
        
        if usage_stats['writes'] > usage_stats['max_writes'] * 0.8:
            self.writes_progress.setStyleSheet("""
                QProgressBar::chunk { background-color: #ef4444; }
            """)
        elif usage_stats['writes'] > usage_stats['max_writes'] * 0.6:
            self.writes_progress.setStyleSheet("""
                QProgressBar::chunk { background-color: #f59e0b; }
            """)
