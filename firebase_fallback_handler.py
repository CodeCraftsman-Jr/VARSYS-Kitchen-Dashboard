#!/usr/bin/env python3
"""
Firebase Fallback Handler
Provides graceful fallback when Firebase modules are missing in the executable
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt

class FirebaseFallbackHandler:
    """Handles missing Firebase dependencies gracefully"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.firebase_available = self.check_firebase_availability()
    
    def check_firebase_availability(self) -> bool:
        """Check if Firebase modules are available"""
        try:
            import firebase_admin
            import pyrebase
            import jwt
            import cryptography
            return True
        except ImportError as e:
            self.logger.warning(f"Firebase modules not available: {e}")
            return False
    
    def get_firebase_status(self) -> Dict[str, Any]:
        """Get detailed Firebase availability status"""
        status = {
            'firebase_admin': False,
            'pyrebase': False,
            'jwt': False,
            'cryptography': False,
            'google_auth': False,
            'missing_modules': []
        }
        
        modules_to_check = [
            ('firebase_admin', 'firebase_admin'),
            ('pyrebase', 'pyrebase'),
            ('jwt', 'jwt'),
            ('cryptography', 'cryptography'),
            ('google_auth', 'google.auth')
        ]
        
        for module_name, import_name in modules_to_check:
            try:
                __import__(import_name)
                status[module_name] = True
            except ImportError:
                status[module_name] = False
                status['missing_modules'].append(module_name)
        
        return status
    
    def show_firebase_missing_dialog(self, parent=None) -> bool:
        """Show user-friendly dialog when Firebase is missing"""
        dialog = QDialog(parent)
        dialog.setWindowTitle("Firebase Setup Required")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("Firebase Authentication Required")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f;")
        layout.addWidget(title)
        
        # Main message
        message = QLabel("""
The Kitchen Dashboard requires Firebase for cloud synchronization and authentication.

This appears to be a distribution issue where Firebase modules were not properly included in the executable.
        """)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Status information
        status = self.get_firebase_status()
        status_text = QTextEdit()
        status_text.setReadOnly(True)
        status_text.setMaximumHeight(150)
        
        status_info = "Firebase Module Status:\n\n"
        for module, available in status.items():
            if module != 'missing_modules':
                status_icon = "✅" if available else "❌"
                status_info += f"{status_icon} {module}: {'Available' if available else 'Missing'}\n"
        
        if status['missing_modules']:
            status_info += f"\nMissing modules: {', '.join(status['missing_modules'])}"
        
        status_text.setPlainText(status_info)
        layout.addWidget(status_text)
        
        # Solutions
        solutions = QLabel("""
<b>Solutions:</b><br>
1. <b>For Developers:</b> Rebuild the executable with proper Firebase inclusion<br>
2. <b>For Users:</b> Contact the application developer for a corrected version<br>
3. <b>Temporary:</b> Use offline mode (limited functionality)
        """)
        solutions.setWordWrap(True)
        layout.addWidget(solutions)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        offline_button = QPushButton("Continue in Offline Mode")
        offline_button.clicked.connect(lambda: dialog.done(1))
        button_layout.addWidget(offline_button)
        
        exit_button = QPushButton("Exit Application")
        exit_button.clicked.connect(lambda: dialog.done(0))
        button_layout.addWidget(exit_button)
        
        layout.addLayout(button_layout)
        
        result = dialog.exec()
        return result == 1  # True if user chose offline mode
    
    def create_offline_firebase_manager(self):
        """Create a mock Firebase manager for offline operation"""
        return OfflineFirebaseManager()

class OfflineFirebaseManager:
    """Mock Firebase manager for offline operation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Running in offline mode - Firebase features disabled")
    
    def is_authenticated(self) -> bool:
        return False
    
    def is_configured(self) -> bool:
        return False
    
    def authenticate_user(self, email: str, password: str) -> bool:
        return False
    
    def sync_data_to_cloud(self, data: Dict) -> Optional[str]:
        self.logger.warning("Cloud sync not available in offline mode")
        return None
    
    def get_database_status(self) -> Dict[str, Any]:
        return {
            'database_available': False,
            'authentication_available': False,
            'user_authenticated': False,
            'offline_mode': True,
            'error_message': 'Running in offline mode - Firebase not available'
        }

def check_and_handle_firebase_requirements(parent=None) -> tuple[bool, Any]:
    """
    Check Firebase requirements and handle missing dependencies
    
    Returns:
        tuple: (firebase_available, firebase_manager_or_fallback)
    """
    handler = FirebaseFallbackHandler()
    
    if handler.firebase_available:
        # Firebase is available, return normal manager
        try:
            from modules.optimized_firebase_manager import get_optimized_firebase_manager
            firebase_manager = get_optimized_firebase_manager()
            return True, firebase_manager
        except Exception as e:
            logging.getLogger(__name__).error(f"Error creating Firebase manager: {e}")
            # Fall through to offline mode
    
    # Firebase not available, show dialog and offer offline mode
    use_offline = handler.show_firebase_missing_dialog(parent)
    
    if use_offline:
        offline_manager = handler.create_offline_firebase_manager()
        return False, offline_manager
    else:
        # User chose to exit
        sys.exit(0)

# Global fallback handler instance
_fallback_handler = None

def get_firebase_fallback_handler() -> FirebaseFallbackHandler:
    """Get the global Firebase fallback handler instance"""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FirebaseFallbackHandler()
    return _fallback_handler
