"""
VARSYS Solutions - Kitchen Dashboard
Enhanced Configuration Management System

Professional configuration management for deployment and distribution
"""

import os
import json
from pathlib import Path
from __version__ import FIREBASE_ENABLED, get_version_info

class VARSYSConfig:
    """Enhanced configuration management for VARSYS Solutions software"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.version_info = get_version_info()
        self._load_config()
        self._ensure_directories()
    
    def _load_config(self):
        """Load configuration from file or use defaults"""
        config_file = self.base_dir / "varsys_app_config.json"
        
        # Default configuration for VARSYS Solutions
        self.defaults = {
            # Company and product info
            "company_name": self.version_info["company"],
            "product_name": self.version_info["product"],
            "app_version": self.version_info["version"],
            "build_number": self.version_info["build"],
            "copyright": self.version_info["copyright"],
            "website": self.version_info["website"],
            "support_email": self.version_info["support_email"],
            
            # Release information
            "release_type": self.version_info["release_type"],
            "is_beta": self.version_info["is_beta"],
            "is_development": self.version_info["is_development"],
            
            # Paths
            "data_dir": "data",
            "logs_dir": "logs", 
            "assets_dir": "assets",
            "backup_dir": "data_backup",
            "releases_dir": "releases",
            "temp_dir": "temp",
            
            # UI settings
            "window_width": 1600,
            "window_height": 1000,
            "min_window_width": 1400,
            "min_window_height": 900,
            "theme": "modern",
            "enable_animations": True,
            "enable_tooltips": True,
            
            # Currency settings
            "default_currency": "₹",
            "available_currencies": {
                "₹": "INR - Indian Rupee",
                "$": "USD - US Dollar", 
                "€": "EUR - Euro",
                "£": "GBP - British Pound"
            },
            
            # Performance settings
            "auto_refresh_interval": 10000,  # milliseconds
            "data_backup_interval": 3600,    # seconds
            "chunk_size": 1000,
            "max_memory_usage": 512 * 1024 * 1024,  # 512MB
            "enable_performance_monitoring": True,
            "enable_caching": True,
            
            # Feature flags (ecosystem ready)
            "firebase_enabled": FIREBASE_ENABLED,
            "subscription_required": self.version_info["subscription_required"],
            "multi_user_support": self.version_info["multi_user_support"],
            "enable_ai_features": True,
            "enable_advanced_analytics": True,
            "enable_export_features": True,
            "enable_backup_features": True,
            "enable_cloud_sync": FIREBASE_ENABLED,
            "enable_offline_mode": True,
            
            # Update system settings
            "check_for_updates": True,
            "update_check_interval": 24,  # hours
            "auto_download_updates": False,
            "update_channel": "stable",  # stable, beta, alpha
            "github_repo": "VARSYS-Solutions/Kitchen-Dashboard",
            
            # Security settings
            "session_timeout": 3600,  # seconds
            "enable_data_encryption": False,  # Future version
            "require_authentication": FIREBASE_ENABLED,
            "enable_audit_logging": True,
            "max_login_attempts": 3,
            
            # Logging settings
            "log_level": "INFO",
            "log_file_max_size": 10 * 1024 * 1024,  # 10MB
            "log_file_backup_count": 5,
            "enable_debug_logging": False,
            "log_to_file": True,
            "log_to_console": True,
            
            # Export settings
            "export_formats": ["csv", "xlsx", "json", "pdf"],
            "default_export_format": "csv",
            "enable_bulk_export": True,
            "max_export_records": 10000,
            
            # Notification settings
            "enable_notifications": True,
            "notification_duration": 5000,  # milliseconds
            "enable_sound_notifications": False,
            "notification_position": "top_right",
            
            # Data management
            "auto_backup_enabled": True,
            "backup_retention_days": 30,
            "data_validation_enabled": True,
            "enable_data_compression": False,
            
            # Development and debugging
            "debug_mode": False,
            "enable_profiling": False,
            "mock_data_enabled": False,
            "enable_test_mode": False,
            
            # Ecosystem integration (future)
            "ecosystem_integration_enabled": False,
            "api_access_enabled": False,
            "third_party_integrations": [],
            
            # Branding
            "show_company_branding": True,
            "enable_custom_themes": False,
            "allow_theme_customization": False
        }
        
        # Load from file if exists
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self.defaults.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load VARSYS config file: {e}")
        
        # Set attributes
        for key, value in self.defaults.items():
            setattr(self, key, value)
    
    def _ensure_directories(self):
        """Create necessary directories"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.assets_dir,
            self.backup_dir,
            self.releases_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(exist_ok=True)
    
    def save_config(self):
        """Save current configuration to file"""
        config_file = self.base_dir / "varsys_app_config.json"
        
        # Get current config
        current_config = {}
        for key in self.defaults.keys():
            current_config[key] = getattr(self, key)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving VARSYS config: {e}")
            return False
    
    def get_path(self, path_name):
        """Get absolute path for a configured directory"""
        relative_path = getattr(self, f"{path_name}_dir", path_name)
        return self.base_dir / relative_path
    
    def update_setting(self, key, value):
        """Update a configuration setting"""
        if hasattr(self, key):
            setattr(self, key, value)
            return True
        return False
    
    def get_version_string(self):
        """Get formatted version string"""
        return f"{self.product_name} v{self.app_version}"
    
    def get_full_title(self):
        """Get full application title"""
        return f"{self.product_name} v{self.app_version} - {self.company_name}"
    
    def is_feature_enabled(self, feature_name):
        """Check if a feature is enabled"""
        return getattr(self, f"enable_{feature_name}", False)
    
    def get_update_url(self):
        """Get update check URL"""
        return f"https://api.github.com/repos/{self.github_repo}/releases/latest"
    
    def get_download_url(self, version_tag):
        """Get download URL for a specific version"""
        return f"https://github.com/{self.github_repo}/releases/download/{version_tag}"
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        for key, value in self.defaults.items():
            setattr(self, key, value)
    
    def export_config(self, file_path):
        """Export configuration to a file"""
        try:
            config_data = {key: getattr(self, key) for key in self.defaults.keys()}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, file_path):
        """Import configuration from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for key, value in config_data.items():
                if key in self.defaults:
                    setattr(self, key, value)
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False

# Global VARSYS configuration instance
varsys_config = VARSYSConfig()

# Convenience functions
def get_varsys_config():
    """Get the global VARSYS configuration instance"""
    return varsys_config

def get_company_info():
    """Get company information"""
    return {
        "name": varsys_config.company_name,
        "website": varsys_config.website,
        "support": varsys_config.support_email,
        "copyright": varsys_config.copyright
    }

def get_product_info():
    """Get product information"""
    return {
        "name": varsys_config.product_name,
        "version": varsys_config.app_version,
        "build": varsys_config.build_number,
        "release_type": varsys_config.release_type
    }

# Export commonly used settings for backward compatibility
VARSYS_COMPANY = varsys_config.company_name
VARSYS_PRODUCT = varsys_config.product_name
VARSYS_VERSION = varsys_config.app_version
VARSYS_WEBSITE = varsys_config.website
VARSYS_SUPPORT = varsys_config.support_email
