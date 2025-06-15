#!/usr/bin/env python3
"""
Firebase Status Widget
Provides real-time Firebase connection status and diagnostics
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTextEdit, QProgressBar,
                             QMessageBox, QDialog)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
import json
from datetime import datetime

class FirebaseStatusWidget(QWidget):
    """Widget to display Firebase connection status and provide controls"""
    
    # Signals
    status_updated = Signal(dict)
    reconnect_requested = Signal()
    
    def __init__(self, firebase_manager=None, parent=None):
        super().__init__(parent)
        self.firebase_manager = firebase_manager
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Status group
        status_group = QGroupBox("Firebase Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        # Main status label
        self.status_label = QLabel("❓ Checking Firebase status...")
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.status_label.setStyleSheet("color: #6b7280; padding: 8px;")
        status_layout.addWidget(self.status_label)
        
        # Details label
        self.details_label = QLabel("Initializing...")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: #6b7280; padding: 4px 8px;")
        status_layout.addWidget(self.details_label)
        
        # Component status
        components_layout = QHBoxLayout()
        
        self.admin_status = QLabel("Admin SDK: ❓")
        self.admin_status.setStyleSheet("padding: 2px 4px;")
        components_layout.addWidget(self.admin_status)
        
        self.db_status = QLabel("Database: ❓")
        self.db_status.setStyleSheet("padding: 2px 4px;")
        components_layout.addWidget(self.db_status)
        
        self.auth_status = QLabel("Auth: ❓")
        self.auth_status.setStyleSheet("padding: 2px 4px;")
        components_layout.addWidget(self.auth_status)
        
        self.user_status = QLabel("User: ❓")
        self.user_status.setStyleSheet("padding: 2px 4px;")
        components_layout.addWidget(self.user_status)
        
        status_layout.addLayout(components_layout)
        
        layout.addWidget(status_group)
        
        # Controls group
        controls_group = QGroupBox("Firebase Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Test connection button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        controls_layout.addWidget(self.test_btn)
        
        # Reconnect button
        self.reconnect_btn = QPushButton("Reconnect")
        self.reconnect_btn.clicked.connect(self.reconnect)
        controls_layout.addWidget(self.reconnect_btn)
        
        # Diagnostics button
        self.diagnostics_btn = QPushButton("Diagnostics")
        self.diagnostics_btn.clicked.connect(self.show_diagnostics)
        controls_layout.addWidget(self.diagnostics_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_status)
        controls_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(controls_group)
        
        # Last updated
        self.last_updated_label = QLabel("Last updated: Never")
        self.last_updated_label.setStyleSheet("color: #9ca3af; font-size: 10px; padding: 4px;")
        layout.addWidget(self.last_updated_label)
        
    def setup_timer(self):
        """Setup automatic status refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial refresh
        self.refresh_status()
    
    def set_firebase_manager(self, firebase_manager):
        """Set the Firebase manager instance"""
        self.firebase_manager = firebase_manager
        self.refresh_status()
    
    def refresh_status(self):
        """Refresh Firebase status"""
        try:
            if not self.firebase_manager:
                self.update_status({
                    'display_text': '❌ Firebase Manager Not Available',
                    'style': 'color: #ef4444; font-weight: bold;',
                    'details': 'Firebase manager is not initialized',
                    'components': {}
                })
                return
            
            # Get diagnostics
            if hasattr(self.firebase_manager, 'get_connection_diagnostics'):
                diagnostics = self.firebase_manager.get_connection_diagnostics()
                
                # Convert diagnostics to status format
                overall_status = diagnostics.get('overall_status', 'unknown')
                components = diagnostics.get('components', {})
                
                status = self.convert_diagnostics_to_status(overall_status, components, diagnostics)
                self.update_status(status)
            else:
                # Fallback status check
                self.update_status({
                    'display_text': '⚠️ Limited Firebase Status Available',
                    'style': 'color: #f59e0b; font-weight: bold;',
                    'details': 'Firebase manager does not support full diagnostics',
                    'components': {}
                })
            
            # Update last updated time
            self.last_updated_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.update_status({
                'display_text': f'❌ Status Check Error',
                'style': 'color: #ef4444; font-weight: bold;',
                'details': f'Error checking Firebase status: {str(e)}',
                'components': {}
            })
    
    def convert_diagnostics_to_status(self, overall_status, components, diagnostics):
        """Convert diagnostics to status format"""
        status = {
            'components': components,
            'diagnostics': diagnostics
        }
        
        if overall_status == 'fully_connected':
            user_email = components.get('user_session', {}).get('user_email', 'Unknown')
            status.update({
                'display_text': f'✅ Firebase Fully Connected',
                'style': 'color: #10b981; font-weight: bold;',
                'details': f'All services operational - User: {user_email}'
            })
        elif overall_status == 'auth_only':
            status.update({
                'display_text': '⚠️ Firebase Auth Only',
                'style': 'color: #f59e0b; font-weight: bold;',
                'details': 'Authentication working but database connection failed'
            })
        elif overall_status == 'database_only':
            status.update({
                'display_text': '⚠️ Firebase Database Only',
                'style': 'color: #f59e0b; font-weight: bold;',
                'details': 'Database connected but authentication unavailable'
            })
        elif overall_status == 'disconnected':
            status.update({
                'display_text': '❌ Firebase Disconnected',
                'style': 'color: #ef4444; font-weight: bold;',
                'details': 'No Firebase services available'
            })
        elif overall_status == 'error':
            status.update({
                'display_text': '❌ Firebase Error State',
                'style': 'color: #ef4444; font-weight: bold;',
                'details': 'Firebase services encountered errors'
            })
        else:
            status.update({
                'display_text': '❓ Firebase Status Unknown',
                'style': 'color: #6b7280; font-weight: bold;',
                'details': 'Unable to determine Firebase status'
            })
        
        return status
    
    def update_status(self, status):
        """Update the status display"""
        # Update main status
        self.status_label.setText(status['display_text'])
        self.status_label.setStyleSheet(status['style'] + "; padding: 8px;")
        
        # Update details
        self.details_label.setText(status.get('details', ''))
        
        # Update component status
        components = status.get('components', {})
        
        admin_sdk = components.get('admin_sdk', {})
        self.admin_status.setText(f"Admin SDK: {'✅' if admin_sdk.get('available') else '❌'}")
        
        firestore = components.get('firestore_database', {})
        db_icon = '✅' if firestore.get('available') and firestore.get('connection_test') else '❌'
        self.db_status.setText(f"Database: {db_icon}")
        
        auth = components.get('pyrebase_auth', {})
        self.auth_status.setText(f"Auth: {'✅' if auth.get('available') else '❌'}")
        
        session = components.get('user_session', {})
        self.user_status.setText(f"User: {'✅' if session.get('authenticated') else '❌'}")
        
        # Emit status update signal
        self.status_updated.emit(status)
    
    def test_connection(self):
        """Test Firebase connection"""
        try:
            if not self.firebase_manager:
                QMessageBox.warning(self, "Firebase Test", "Firebase manager not available")
                return
            
            # Show progress
            self.test_btn.setText("Testing...")
            self.test_btn.setEnabled(False)
            
            # Test database connection
            if hasattr(self.firebase_manager, 'test_database_connection'):
                db_test = self.firebase_manager.test_database_connection()
                auth_test = self.firebase_manager.is_authenticated()
                
                if db_test and auth_test:
                    QMessageBox.information(self, "Firebase Test", "✅ All Firebase services are working correctly!")
                elif db_test:
                    QMessageBox.warning(self, "Firebase Test", "⚠️ Database connection works but user not authenticated")
                elif auth_test:
                    QMessageBox.warning(self, "Firebase Test", "⚠️ User authenticated but database connection failed")
                else:
                    QMessageBox.critical(self, "Firebase Test", "❌ Firebase connection test failed")
            else:
                QMessageBox.warning(self, "Firebase Test", "Firebase test functionality not available")
            
            # Refresh status after test
            self.refresh_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Firebase Test", f"Error during test: {str(e)}")
        finally:
            self.test_btn.setText("Test Connection")
            self.test_btn.setEnabled(True)
    
    def reconnect(self):
        """Reconnect to Firebase"""
        try:
            if not self.firebase_manager:
                QMessageBox.warning(self, "Firebase Reconnect", "Firebase manager not available")
                return
            
            # Show progress
            self.reconnect_btn.setText("Reconnecting...")
            self.reconnect_btn.setEnabled(False)
            
            # Attempt reconnection
            if hasattr(self.firebase_manager, 'reinitialize_firebase'):
                success = self.firebase_manager.reinitialize_firebase()
            else:
                success = self.firebase_manager.reinitialize_database()
            
            if success:
                QMessageBox.information(self, "Firebase Reconnect", "✅ Firebase reconnection successful!")
            else:
                QMessageBox.warning(self, "Firebase Reconnect", "⚠️ Firebase reconnection failed")
            
            # Refresh status after reconnect
            self.refresh_status()
            
            # Emit reconnect signal
            self.reconnect_requested.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Firebase Reconnect", f"Error during reconnection: {str(e)}")
        finally:
            self.reconnect_btn.setText("Reconnect")
            self.reconnect_btn.setEnabled(True)
    
    def show_diagnostics(self):
        """Show detailed Firebase diagnostics"""
        try:
            if not self.firebase_manager:
                QMessageBox.warning(self, "Firebase Diagnostics", "Firebase manager not available")
                return
            
            # Get diagnostics
            if hasattr(self.firebase_manager, 'get_connection_diagnostics'):
                diagnostics = self.firebase_manager.get_connection_diagnostics()
                
                # Create diagnostics dialog
                dialog = QDialog(self)
                dialog.setWindowTitle("Firebase Diagnostics")
                dialog.resize(600, 500)
                
                layout = QVBoxLayout(dialog)
                
                # Diagnostics text
                diag_text = QTextEdit()
                diag_content = json.dumps(diagnostics, indent=2)
                diag_text.setPlainText(diag_content)
                diag_text.setReadOnly(True)
                layout.addWidget(diag_text)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec()
            else:
                QMessageBox.information(self, "Firebase Diagnostics", "Detailed diagnostics not available")
                
        except Exception as e:
            QMessageBox.critical(self, "Firebase Diagnostics", f"Error showing diagnostics: {str(e)}")
