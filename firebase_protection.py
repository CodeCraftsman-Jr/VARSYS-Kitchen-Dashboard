#!/usr/bin/env python3
"""
Advanced Firebase Protection System for VARSYS Kitchen Dashboard
Prevents users from accessing, modifying, or bypassing Firebase configuration
"""

import os
import json
import base64
import hashlib
import hmac
import time
from typing import Dict, Optional, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from license_manager import license_manager

class SecureFirebaseVault:
    """Ultra-secure Firebase configuration vault"""
    
    def __init__(self):
        # These secrets will be replaced during secure build process
        self.master_secret = os.getenv('VARSYS_FIREBASE_SECRET', "VARSYS_FIREBASE_MASTER_KEY_2025_YOUR_UNIQUE_KEY")
        self.vault_salt = b"varsys_firebase_vault_salt_2025_secure"
        self.integrity_key = os.getenv('VARSYS_INTEGRITY_KEY', "VARSYS_INTEGRITY_CHECK_2025_YOUR_UNIQUE_KEY")
        
        # Multiple layers of protection
        self.vault_file = ".firebase_vault.dat"
        self.checksum_file = ".firebase_checksum.dat"
        self.access_log_file = ".firebase_access.log"
        
    def _derive_encryption_key(self, additional_entropy: str = "") -> bytes:
        """Derive encryption key from multiple sources"""
        # Combine multiple entropy sources
        entropy_sources = [
            self.master_secret,
            license_manager.machine_id,
            license_manager.app_secret,
            additional_entropy,
            str(int(time.time() // 86400))  # Changes daily
        ]
        
        combined_entropy = "".join(entropy_sources).encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.vault_salt,
            iterations=200000,  # High iteration count for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(combined_entropy))
        return key
    
    def _create_integrity_hash(self, data: bytes) -> str:
        """Create integrity hash to detect tampering"""
        integrity_data = data + self.integrity_key.encode() + license_manager.machine_id.encode()
        return hashlib.sha512(integrity_data).hexdigest()
    
    def _verify_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Verify data integrity"""
        actual_hash = self._create_integrity_hash(data)
        return hmac.compare_digest(actual_hash, expected_hash)
    
    def _log_access_attempt(self, action: str, success: bool, details: str = ""):
        """Log all access attempts for security monitoring"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                'timestamp': timestamp,
                'action': action,
                'success': success,
                'machine_id': license_manager.machine_id,
                'details': details
            }
            
            # Append to access log
            with open(self.access_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception:
            pass  # Silent logging failure
    
    def store_firebase_config(self, firebase_config: Dict) -> bool:
        """Store Firebase config with maximum security"""
        try:
            # Verify license first
            if not license_manager.is_feature_enabled('firebase_sync'):
                self._log_access_attempt("store_config", False, "Invalid license")
                raise PermissionError("Valid license required for Firebase configuration")
            
            # Prepare secure payload
            payload = {
                'firebase_config': firebase_config,
                'license_machine_id': license_manager.machine_id,
                'creation_time': time.time(),
                'license_signature': self._create_license_signature(firebase_config),
                'access_count': 0
            }
            
            # Serialize and encrypt
            payload_json = json.dumps(payload, sort_keys=True)
            payload_bytes = payload_json.encode()
            
            # Create integrity hash
            integrity_hash = self._create_integrity_hash(payload_bytes)
            
            # Encrypt with derived key
            encryption_key = self._derive_encryption_key("firebase_store")
            fernet = Fernet(encryption_key)
            encrypted_payload = fernet.encrypt(payload_bytes)
            
            # Create final vault structure
            vault_data = {
                'encrypted_payload': base64.b64encode(encrypted_payload).decode(),
                'integrity_hash': integrity_hash,
                'vault_version': '2.0',
                'protection_level': 'maximum'
            }
            
            # Write vault file
            with open(self.vault_file, 'w') as f:
                json.dump(vault_data, f, separators=(',', ':'))  # Compact format
            
            # Write checksum file separately
            vault_checksum = hashlib.sha256(json.dumps(vault_data).encode()).hexdigest()
            with open(self.checksum_file, 'w') as f:
                f.write(vault_checksum)
            
            self._log_access_attempt("store_config", True, "Firebase config stored securely")
            return True
            
        except Exception as e:
            self._log_access_attempt("store_config", False, str(e))
            return False
    
    def retrieve_firebase_config(self) -> Optional[Dict]:
        """Retrieve Firebase config with security verification"""
        try:
            # Verify license
            if not license_manager.is_feature_enabled('firebase_sync'):
                self._log_access_attempt("retrieve_config", False, "Invalid license")
                return None
            
            # Check if vault files exist
            if not os.path.exists(self.vault_file) or not os.path.exists(self.checksum_file):
                self._log_access_attempt("retrieve_config", False, "Vault files missing")
                return None
            
            # Verify vault file integrity
            with open(self.vault_file, 'r') as f:
                vault_data = json.load(f)
            
            with open(self.checksum_file, 'r') as f:
                expected_checksum = f.read().strip()
            
            actual_checksum = hashlib.sha256(json.dumps(vault_data).encode()).hexdigest()
            if not hmac.compare_digest(actual_checksum, expected_checksum):
                self._log_access_attempt("retrieve_config", False, "Vault checksum mismatch")
                return None
            
            # Decrypt payload
            encrypted_payload = base64.b64decode(vault_data['encrypted_payload'])
            integrity_hash = vault_data['integrity_hash']
            
            encryption_key = self._derive_encryption_key("firebase_store")
            fernet = Fernet(encryption_key)
            decrypted_payload = fernet.decrypt(encrypted_payload)
            
            # Verify integrity
            if not self._verify_integrity(decrypted_payload, integrity_hash):
                self._log_access_attempt("retrieve_config", False, "Integrity verification failed")
                return None
            
            # Parse payload
            payload = json.loads(decrypted_payload.decode())
            
            # Verify machine ID
            if payload.get('license_machine_id') != license_manager.machine_id:
                self._log_access_attempt("retrieve_config", False, "Machine ID mismatch")
                return None
            
            # Verify license signature
            firebase_config = payload.get('firebase_config', {})
            if not self._verify_license_signature(firebase_config, payload.get('license_signature', '')):
                self._log_access_attempt("retrieve_config", False, "License signature invalid")
                return None
            
            # Update access count (anti-tampering measure)
            payload['access_count'] = payload.get('access_count', 0) + 1
            self._update_access_count(payload)
            
            self._log_access_attempt("retrieve_config", True, "Firebase config retrieved")
            return firebase_config
            
        except Exception as e:
            self._log_access_attempt("retrieve_config", False, str(e))
            return None
    
    def _create_license_signature(self, firebase_config: Dict) -> str:
        """Create license-based signature for Firebase config"""
        signature_data = {
            'firebase_config': firebase_config,
            'machine_id': license_manager.machine_id,
            'license_key': getattr(license_manager, 'current_license_key', 'unknown')
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        signature = hmac.new(
            self.master_secret.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _verify_license_signature(self, firebase_config: Dict, signature: str) -> bool:
        """Verify license signature"""
        expected_signature = self._create_license_signature(firebase_config)
        return hmac.compare_digest(signature, expected_signature)
    
    def _update_access_count(self, payload: Dict):
        """Update access count in vault (anti-tampering)"""
        try:
            # Re-encrypt and store updated payload
            payload_json = json.dumps(payload, sort_keys=True)
            payload_bytes = payload_json.encode()
            
            integrity_hash = self._create_integrity_hash(payload_bytes)
            encryption_key = self._derive_encryption_key("firebase_store")
            fernet = Fernet(encryption_key)
            encrypted_payload = fernet.encrypt(payload_bytes)
            
            vault_data = {
                'encrypted_payload': base64.b64encode(encrypted_payload).decode(),
                'integrity_hash': integrity_hash,
                'vault_version': '2.0',
                'protection_level': 'maximum'
            }
            
            with open(self.vault_file, 'w') as f:
                json.dump(vault_data, f, separators=(',', ':'))
            
            vault_checksum = hashlib.sha256(json.dumps(vault_data).encode()).hexdigest()
            with open(self.checksum_file, 'w') as f:
                f.write(vault_checksum)
                
        except Exception:
            pass  # Silent failure for access count update
    
    def is_firebase_accessible(self) -> bool:
        """Check if Firebase is accessible with current license"""
        return (license_manager.is_feature_enabled('firebase_sync') and 
                self.retrieve_firebase_config() is not None)
    
    def destroy_vault(self) -> bool:
        """Securely destroy Firebase vault (for license deactivation)"""
        try:
            files_to_remove = [self.vault_file, self.checksum_file]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    # Overwrite with random data before deletion
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(1024 * 1024))  # 1MB of random data
                    os.remove(file_path)
            
            self._log_access_attempt("destroy_vault", True, "Vault destroyed")
            return True
            
        except Exception as e:
            self._log_access_attempt("destroy_vault", False, str(e))
            return False

class ProtectedFirebaseManager:
    """Firebase manager with ultra-secure protection"""
    
    def __init__(self):
        self.vault = SecureFirebaseVault()
        self.firebase_app = None
        self.firestore_db = None
        self._access_attempts = 0
        self._max_access_attempts = 5
    
    def initialize_firebase(self) -> Tuple[bool, str]:
        """Initialize Firebase with maximum security"""
        try:
            # Rate limiting
            self._access_attempts += 1
            if self._access_attempts > self._max_access_attempts:
                return False, "Too many access attempts"
            
            # Verify license
            if not license_manager.is_feature_enabled('firebase_sync'):
                return False, "Firebase sync requires valid license"
            
            # Retrieve protected config
            config = self.vault.retrieve_firebase_config()
            if not config:
                return False, "No valid Firebase configuration found"
            
            # Initialize Firebase with protected config
            # (Add actual Firebase initialization here)
            self.firebase_app = "initialized"  # Placeholder
            self.firestore_db = "connected"    # Placeholder
            
            return True, "Firebase initialized successfully"
            
        except Exception as e:
            return False, f"Firebase initialization failed: {str(e)}"
    
    def sync_data_to_firebase(self, data: Dict) -> Tuple[bool, str]:
        """Sync data to Firebase with protection"""
        try:
            if not license_manager.is_feature_enabled('firebase_sync'):
                return False, "Firebase sync requires valid license"
            
            if not self.is_connected():
                success, message = self.initialize_firebase()
                if not success:
                    return False, f"Firebase not available: {message}"
            
            # Perform actual sync (simplified)
            # Add your Firebase sync logic here
            
            return True, "Data synced successfully"
            
        except Exception as e:
            return False, f"Sync failed: {str(e)}"
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return (self.firebase_app is not None and 
                self.firestore_db is not None and
                self.vault.is_firebase_accessible())

# Global protected Firebase instance
protected_firebase_manager = ProtectedFirebaseManager()

def get_protected_firebase_manager() -> ProtectedFirebaseManager:
    """Get the protected Firebase manager"""
    return protected_firebase_manager

def setup_secure_firebase(firebase_config: Dict) -> bool:
    """Setup Firebase with maximum security"""
    try:
        vault = SecureFirebaseVault()
        return vault.store_firebase_config(firebase_config)
    except Exception:
        return False

def require_firebase_access(func):
    """Decorator requiring Firebase access"""
    def wrapper(*args, **kwargs):
        if not license_manager.is_feature_enabled('firebase_sync'):
            raise PermissionError("Firebase access requires valid license")
        
        vault = SecureFirebaseVault()
        if not vault.is_firebase_accessible():
            raise PermissionError("Firebase configuration not accessible")
        
        return func(*args, **kwargs)
    return wrapper
