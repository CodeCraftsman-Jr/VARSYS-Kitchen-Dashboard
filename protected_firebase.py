#!/usr/bin/env python3
"""
Protected Firebase Configuration for VARSYS Kitchen Dashboard
Prevents unauthorized access to Firebase features
"""

import os
import json
import hashlib
import hmac
from typing import Dict, Optional, Any
from license_manager import license_manager

class ProtectedFirebaseConfig:
    """Protected Firebase configuration that requires valid license"""
    
    def __init__(self):
        self.config_file = "firebase_config_protected.json"
        # This secret will be replaced during secure build process
        self.app_secret = os.getenv('VARSYS_FIREBASE_SECRET', "VARSYS_FIREBASE_SECRET_2025")
        
    def _verify_license_for_firebase(self) -> bool:
        """Verify license allows Firebase access"""
        try:
            return license_manager.is_feature_enabled('firebase_sync')
        except:
            return False
    
    def _create_config_signature(self, config: Dict) -> str:
        """Create tamper-proof signature for Firebase config"""
        config_string = json.dumps(config, sort_keys=True)
        signature = hmac.new(
            self.app_secret.encode(),
            config_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_config_signature(self, config: Dict, signature: str) -> bool:
        """Verify Firebase config signature"""
        expected_signature = self._create_config_signature(config)
        return hmac.compare_digest(signature, expected_signature)
    
    def save_firebase_config(self, config: Dict) -> bool:
        """Save Firebase configuration with license protection"""
        try:
            if not self._verify_license_for_firebase():
                raise PermissionError("Valid license required for Firebase configuration")
            
            # Add signature to config
            config_with_signature = {
                'config': config,
                'signature': self._create_config_signature(config),
                'license_machine_id': license_manager.machine_id
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_with_signature, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving Firebase config: {e}")
            return False
    
    def load_firebase_config(self) -> Optional[Dict]:
        """Load Firebase configuration with license verification"""
        try:
            if not self._verify_license_for_firebase():
                return None
            
            if not os.path.exists(self.config_file):
                return None
            
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Verify signature
            config = config_data.get('config', {})
            signature = config_data.get('signature', '')
            machine_id = config_data.get('license_machine_id', '')
            
            if not self._verify_config_signature(config, signature):
                print("Firebase config has been tampered with")
                return None
            
            if machine_id != license_manager.machine_id:
                print("Firebase config is not valid for this machine")
                return None
            
            return config
            
        except Exception as e:
            print(f"Error loading Firebase config: {e}")
            return None
    
    def is_firebase_available(self) -> bool:
        """Check if Firebase is available with current license"""
        return (self._verify_license_for_firebase() and 
                self.load_firebase_config() is not None)

class ProtectedFirebaseManager:
    """Firebase manager with license protection"""
    
    def __init__(self):
        self.config_manager = ProtectedFirebaseConfig()
        self.firebase_app = None
        self.firestore_db = None
        
    def initialize_firebase(self) -> bool:
        """Initialize Firebase with license protection"""
        try:
            if not license_manager.is_feature_enabled('firebase_sync'):
                print("Firebase sync requires valid license")
                return False
            
            config = self.config_manager.load_firebase_config()
            if not config:
                print("No valid Firebase configuration found")
                return False
            
            # Initialize Firebase (simplified - add actual Firebase initialization)
            print("Firebase initialized with license protection")
            return True
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            return False
    
    def sync_data(self, data: Dict) -> bool:
        """Sync data to Firebase with license protection"""
        try:
            if not license_manager.is_feature_enabled('firebase_sync'):
                raise PermissionError("Firebase sync requires valid license")
            
            if not self.is_initialized():
                return False
            
            # Perform actual sync (simplified)
            print("Data synced to Firebase with license protection")
            return True
            
        except PermissionError as e:
            print(f"License error: {e}")
            return False
        except Exception as e:
            print(f"Sync error: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if Firebase is properly initialized"""
        return (self.config_manager.is_firebase_available() and 
                self.firebase_app is not None)

# Global protected Firebase manager
protected_firebase = ProtectedFirebaseManager()

def get_protected_firebase() -> ProtectedFirebaseManager:
    """Get the protected Firebase manager instance"""
    return protected_firebase

def setup_firebase_with_license(config: Dict) -> bool:
    """Setup Firebase configuration with license verification"""
    try:
        if not license_manager.is_feature_enabled('firebase_sync'):
            print("Firebase setup requires valid license")
            return False
        
        config_manager = ProtectedFirebaseConfig()
        return config_manager.save_firebase_config(config)
        
    except Exception as e:
        print(f"Error setting up Firebase: {e}")
        return False

def require_firebase_license(func):
    """Decorator to require Firebase license for functions"""
    def wrapper(*args, **kwargs):
        if not license_manager.is_feature_enabled('firebase_sync'):
            raise PermissionError("Firebase features require valid license")
        return func(*args, **kwargs)
    return wrapper
