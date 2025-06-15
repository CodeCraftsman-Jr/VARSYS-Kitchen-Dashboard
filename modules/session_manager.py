"""
Session Manager for Kitchen Dashboard
Handles automatic login, session persistence, and "Remember Me" functionality
"""

import os
import json
import base64
import logging
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any

class SessionManager(QObject):
    """Manages user sessions and automatic login functionality"""
    
    # Signals
    session_restored = Signal(dict)  # Emitted when session is restored
    session_expired = Signal()       # Emitted when session expires
    
    def __init__(self, app_name="KitchenDashboard"):
        super().__init__()
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        
        # Session storage paths
        self.session_dir = os.path.join(os.path.expanduser("~"), ".kitchen_dashboard")
        self.session_file = os.path.join(self.session_dir, "session.dat")
        self.remember_file = os.path.join(self.session_dir, "remember.dat")
        
        # Ensure session directory exists
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
        
        # Session settings
        self.session_timeout = 24 * 60 * 60  # 24 hours in seconds
        self.remember_timeout = 30 * 24 * 60 * 60  # 30 days in seconds
        
    def _init_encryption(self):
        """Initialize encryption for secure session storage"""
        try:
            # Create machine-specific key
            machine_id = self._get_machine_id()
            salt = (machine_id + self.app_name).encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            self.cipher = Fernet(key)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
            self.cipher = None
    
    def _get_machine_id(self) -> str:
        """Get a machine-specific identifier"""
        try:
            import platform
            machine_info = (
                platform.node() +
                platform.system() +
                os.getenv('USERNAME', '') +
                os.getenv('COMPUTERNAME', '')
            )
            return machine_info
        except:
            return "default_machine_id"
    
    def save_session(self, user_info: Dict[str, Any], remember_me: bool = False) -> bool:
        """Save user session for automatic login"""
        try:
            session_data = {
                'user_info': user_info,
                'timestamp': datetime.now().isoformat(),
                'remember_me': remember_me,
                'app_version': '1.0.6'
            }
            
            # Encrypt and save session
            if self.cipher:
                encrypted_data = self.cipher.encrypt(json.dumps(session_data).encode())
                
                # Save to appropriate file based on remember_me setting
                target_file = self.remember_file if remember_me else self.session_file
                
                with open(target_file, 'wb') as f:
                    f.write(encrypted_data)
                
                self.logger.info(f"Session saved {'with remember me' if remember_me else 'for current session'}")
                return True
            else:
                self.logger.error("Encryption not available, cannot save session")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """Load saved session for automatic login"""
        try:
            # Try to load remember me session first, then regular session
            for session_file in [self.remember_file, self.session_file]:
                if os.path.exists(session_file):
                    session_data = self._load_session_file(session_file)
                    if session_data and self._is_session_valid(session_data):
                        self.logger.info(f"Valid session loaded from {os.path.basename(session_file)}")
                        return session_data
                    elif session_data:
                        self.logger.info(f"Session expired in {os.path.basename(session_file)}")
                        self._delete_session_file(session_file)
            
            self.logger.info("No valid session found")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
            return None
    
    def _load_session_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load and decrypt session file"""
        try:
            if not self.cipher:
                return None
                
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = json.loads(decrypted_data.decode())
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"Failed to load session file {file_path}: {e}")
            return None
    
    def _is_session_valid(self, session_data: Dict[str, Any]) -> bool:
        """Check if session is still valid"""
        try:
            timestamp_str = session_data.get('timestamp')
            if not timestamp_str:
                return False
            
            session_time = datetime.fromisoformat(timestamp_str)
            current_time = datetime.now()
            
            # Check timeout based on remember_me setting
            is_remember_me = session_data.get('remember_me', False)
            timeout = self.remember_timeout if is_remember_me else self.session_timeout
            
            time_diff = (current_time - session_time).total_seconds()
            
            return time_diff < timeout
            
        except Exception as e:
            self.logger.error(f"Error checking session validity: {e}")
            return False
    
    def clear_session(self, clear_remember_me: bool = False):
        """Clear saved session data"""
        try:
            # Always clear regular session
            self._delete_session_file(self.session_file)
            
            # Clear remember me session if requested
            if clear_remember_me:
                self._delete_session_file(self.remember_file)
                self.logger.info("Cleared all saved sessions including remember me")
            else:
                self.logger.info("Cleared current session")
                
        except Exception as e:
            self.logger.error(f"Failed to clear session: {e}")
    
    def _delete_session_file(self, file_path: str):
        """Safely delete session file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.error(f"Failed to delete session file {file_path}: {e}")
    
    def has_saved_session(self) -> bool:
        """Check if there's a saved session available"""
        return (os.path.exists(self.session_file) or 
                os.path.exists(self.remember_file))
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about saved sessions"""
        info = {
            'has_current_session': os.path.exists(self.session_file),
            'has_remember_me_session': os.path.exists(self.remember_file),
            'session_dir': self.session_dir
        }
        
        # Add file timestamps if they exist
        for file_path, key in [(self.session_file, 'current_session_time'), 
                              (self.remember_file, 'remember_me_session_time')]:
            if os.path.exists(file_path):
                try:
                    mtime = os.path.getmtime(file_path)
                    info[key] = datetime.fromtimestamp(mtime).isoformat()
                except:
                    info[key] = "Unknown"
        
        return info
    
    def update_session_activity(self, user_info: Dict[str, Any]):
        """Update session with latest activity"""
        try:
            # Check if we have a remember me session
            if os.path.exists(self.remember_file):
                session_data = self._load_session_file(self.remember_file)
                if session_data and session_data.get('remember_me'):
                    # Update the remember me session with new activity
                    self.save_session(user_info, remember_me=True)
            
            # Always update current session
            self.save_session(user_info, remember_me=False)
            
        except Exception as e:
            self.logger.error(f"Failed to update session activity: {e}")


# Global session manager instance
_session_manager = None

def get_session_manager():
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
