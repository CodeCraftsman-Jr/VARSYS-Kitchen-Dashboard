"""
Firebase Configuration Manager
Manages Firebase configuration, authentication, and cloud sync settings for Kitchen Dashboard v1.0.6
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

@dataclass
class FirebaseConfig:
    """Firebase configuration data class"""
    api_key: str
    auth_domain: str
    database_url: str
    project_id: str
    storage_bucket: str
    messaging_sender_id: str
    app_id: str
    measurement_id: str = ""

@dataclass
class SyncSettings:
    """Cloud sync settings data class"""
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 5
    batch_size: int = 100
    max_retries: int = 3
    conflict_resolution: str = "ask_user"

@dataclass
class SecuritySettings:
    """Security settings data class"""
    require_authentication: bool = True
    session_timeout_hours: int = 24
    auto_logout_on_idle: bool = True
    idle_timeout_minutes: int = 30

class FirebaseConfigManager(QObject):
    """
    Firebase Configuration Manager for Kitchen Dashboard v1.0.6
    
    Features:
    - Firebase configuration management
    - Settings validation
    - Configuration file handling
    - Environment variable support
    """
    
    # Signals
    config_changed = Signal()
    authentication_required = Signal()
    
    def __init__(self, config_file: str = "firebase_config.json"):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        
        # Configuration objects
        self.firebase_config: Optional[FirebaseConfig] = None
        self.sync_settings: Optional[SyncSettings] = None
        self.security_settings: Optional[SecuritySettings] = None
        self.features: Dict[str, bool] = {}
        
        # Load configuration
        self.load_configuration()
    
    def load_configuration(self) -> bool:
        """Load Firebase configuration from file or environment variables"""
        try:
            # Try to load from file first
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Parse Firebase config
                firebase_data = config_data.get('firebase', {})
                if firebase_data:
                    self.firebase_config = FirebaseConfig(
                        api_key=firebase_data.get('apiKey', ''),
                        auth_domain=firebase_data.get('authDomain', ''),
                        database_url=firebase_data.get('databaseURL', ''),
                        project_id=firebase_data.get('projectId', ''),
                        storage_bucket=firebase_data.get('storageBucket', ''),
                        messaging_sender_id=firebase_data.get('messagingSenderId', ''),
                        app_id=firebase_data.get('appId', ''),
                        measurement_id=firebase_data.get('measurementId', '')
                    )
                
                # Parse sync settings
                sync_data = config_data.get('sync_settings', {})
                self.sync_settings = SyncSettings(
                    auto_sync_enabled=sync_data.get('auto_sync_enabled', True),
                    sync_interval_minutes=sync_data.get('sync_interval_minutes', 5),
                    batch_size=sync_data.get('batch_size', 100),
                    max_retries=sync_data.get('max_retries', 3),
                    conflict_resolution=sync_data.get('conflict_resolution', 'ask_user')
                )
                
                # Parse security settings
                security_data = config_data.get('security', {})
                self.security_settings = SecuritySettings(
                    require_authentication=security_data.get('require_authentication', True),
                    session_timeout_hours=security_data.get('session_timeout_hours', 24),
                    auto_logout_on_idle=security_data.get('auto_logout_on_idle', True),
                    idle_timeout_minutes=security_data.get('idle_timeout_minutes', 30)
                )
                
                # Parse features
                self.features = config_data.get('features', {})
                
                self.logger.info("Firebase configuration loaded successfully from file")
                return True
            
            # Try to load from environment variables
            elif self.load_from_environment():
                self.logger.info("Firebase configuration loaded from environment variables")
                return True
            
            else:
                self.logger.warning("No Firebase configuration found")
                self.create_default_config()
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading Firebase configuration: {e}")
            self.create_default_config()
            return False
    
    def load_from_environment(self) -> bool:
        """Load configuration from environment variables"""
        try:
            # Check if required environment variables exist
            required_vars = [
                'FIREBASE_API_KEY',
                'FIREBASE_AUTH_DOMAIN',
                'FIREBASE_PROJECT_ID'
            ]
            
            if not all(os.getenv(var) for var in required_vars):
                return False
            
            # Create Firebase config from environment
            self.firebase_config = FirebaseConfig(
                api_key=os.getenv('FIREBASE_API_KEY', ''),
                auth_domain=os.getenv('FIREBASE_AUTH_DOMAIN', ''),
                database_url=os.getenv('FIREBASE_DATABASE_URL', ''),
                project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
                storage_bucket=os.getenv('FIREBASE_STORAGE_BUCKET', ''),
                messaging_sender_id=os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
                app_id=os.getenv('FIREBASE_APP_ID', ''),
                measurement_id=os.getenv('FIREBASE_MEASUREMENT_ID', '')
            )
            
            # Create default sync and security settings
            self.sync_settings = SyncSettings()
            self.security_settings = SecuritySettings()
            self.features = {
                'authentication': True,
                'cloud_sync': True,
                'real_time_sync': True,
                'offline_support': True,
                'analytics': True
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading from environment: {e}")
            return False
    
    def create_default_config(self):
        """Create default configuration"""
        self.firebase_config = FirebaseConfig(
            api_key="",
            auth_domain="",
            database_url="",
            project_id="",
            storage_bucket="",
            messaging_sender_id="",
            app_id="",
            measurement_id=""
        )
        
        self.sync_settings = SyncSettings()
        self.security_settings = SecuritySettings()
        self.features = {
            'authentication': False,
            'cloud_sync': False,
            'real_time_sync': False,
            'offline_support': True,
            'analytics': False
        }
        
        self.logger.info("Created default Firebase configuration")
    
    def save_configuration(self) -> bool:
        """Save current configuration to file"""
        try:
            config_data = {
                'firebase': {
                    'apiKey': self.firebase_config.api_key if self.firebase_config else '',
                    'authDomain': self.firebase_config.auth_domain if self.firebase_config else '',
                    'databaseURL': self.firebase_config.database_url if self.firebase_config else '',
                    'projectId': self.firebase_config.project_id if self.firebase_config else '',
                    'storageBucket': self.firebase_config.storage_bucket if self.firebase_config else '',
                    'messagingSenderId': self.firebase_config.messaging_sender_id if self.firebase_config else '',
                    'appId': self.firebase_config.app_id if self.firebase_config else '',
                    'measurementId': self.firebase_config.measurement_id if self.firebase_config else ''
                },
                'features': self.features,
                'sync_settings': {
                    'auto_sync_enabled': self.sync_settings.auto_sync_enabled if self.sync_settings else True,
                    'sync_interval_minutes': self.sync_settings.sync_interval_minutes if self.sync_settings else 5,
                    'batch_size': self.sync_settings.batch_size if self.sync_settings else 100,
                    'max_retries': self.sync_settings.max_retries if self.sync_settings else 3,
                    'conflict_resolution': self.sync_settings.conflict_resolution if self.sync_settings else 'ask_user'
                },
                'security': {
                    'require_authentication': self.security_settings.require_authentication if self.security_settings else True,
                    'session_timeout_hours': self.security_settings.session_timeout_hours if self.security_settings else 24,
                    'auto_logout_on_idle': self.security_settings.auto_logout_on_idle if self.security_settings else True,
                    'idle_timeout_minutes': self.security_settings.idle_timeout_minutes if self.security_settings else 30
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info("Firebase configuration saved successfully")
            self.config_changed.emit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving Firebase configuration: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if Firebase is properly configured"""
        if not self.firebase_config:
            return False
        
        required_fields = [
            self.firebase_config.api_key,
            self.firebase_config.auth_domain,
            self.firebase_config.project_id
        ]
        
        return all(field.strip() for field in required_fields)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled"""
        return self.features.get(feature, False)
    
    def get_firebase_config_dict(self) -> Dict[str, str]:
        """Get Firebase configuration as dictionary for pyrebase"""
        if not self.firebase_config:
            return {}
        
        return {
            'apiKey': self.firebase_config.api_key,
            'authDomain': self.firebase_config.auth_domain,
            'databaseURL': self.firebase_config.database_url,
            'projectId': self.firebase_config.project_id,
            'storageBucket': self.firebase_config.storage_bucket,
            'messagingSenderId': self.firebase_config.messaging_sender_id,
            'appId': self.firebase_config.app_id,
            'measurementId': self.firebase_config.measurement_id
        }
    
    def validate_configuration(self) -> tuple[bool, str]:
        """Validate the current configuration"""
        if not self.firebase_config:
            return False, "Firebase configuration not loaded"
        
        if not self.firebase_config.api_key:
            return False, "Firebase API key is required"
        
        if not self.firebase_config.auth_domain:
            return False, "Firebase auth domain is required"
        
        if not self.firebase_config.project_id:
            return False, "Firebase project ID is required"
        
        return True, "Configuration is valid"

# Global configuration manager instance
_config_manager = None

def get_firebase_config_manager() -> FirebaseConfigManager:
    """Get the global Firebase configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = FirebaseConfigManager()
    return _config_manager
