#!/usr/bin/env python3
"""
Commercial License Manager for VARSYS Kitchen Dashboard
Protects against unauthorized access and ensures proper licensing
"""

import os
import json
import hashlib
import hmac
import time
import uuid
import requests
import platform
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class LicenseManager:
    """Manages commercial licensing and prevents unauthorized access"""
    
    def __init__(self):
        self.license_server_url = "https://your-license-server.com/api"  # Your license server
        # This secret will be replaced during secure build process
        self.app_secret = os.getenv('VARSYS_APP_SECRET', "VARSYS_KITCHEN_DASHBOARD_SECRET_2025_YOUR_UNIQUE_KEY")
        self.license_file = "license.dat"
        self.machine_id = self._generate_machine_id()
        self.encryption_key = self._derive_encryption_key()
        
    def _generate_machine_id(self) -> str:
        """Generate unique machine identifier"""
        try:
            # Combine multiple hardware identifiers
            machine_info = {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'node': platform.node(),
            }
            
            # Add MAC address if available
            try:
                import uuid
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,2*6,2)][::-1])
                machine_info['mac'] = mac
            except:
                pass
            
            # Create hash of machine info
            machine_string = json.dumps(machine_info, sort_keys=True)
            machine_hash = hashlib.sha256(machine_string.encode()).hexdigest()
            
            return machine_hash[:32]  # Use first 32 characters
            
        except Exception:
            # Fallback to basic identifier
            return hashlib.sha256(platform.node().encode()).hexdigest()[:32]
    
    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from app secret and machine ID"""
        password = f"{self.app_secret}_{self.machine_id}".encode()
        salt = b"varsys_kitchen_salt_2025"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            f = Fernet(self.encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            raise ValueError("Invalid license data")
    
    def _create_license_signature(self, license_data: Dict) -> str:
        """Create tamper-proof signature for license"""
        # Create signature from critical license data
        signature_data = {
            'user_id': license_data.get('user_id'),
            'email': license_data.get('email'),
            'expires_at': license_data.get('expires_at'),
            'machine_id': license_data.get('machine_id'),
            'license_type': license_data.get('license_type')
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        signature = hmac.new(
            self.app_secret.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _verify_license_signature(self, license_data: Dict) -> bool:
        """Verify license signature to detect tampering"""
        stored_signature = license_data.get('signature')
        if not stored_signature:
            return False
        
        expected_signature = self._create_license_signature(license_data)
        return hmac.compare_digest(stored_signature, expected_signature)
    
    def activate_license(self, license_key: str, user_email: str) -> Tuple[bool, str]:
        """Activate license with your license server"""
        try:
            # Contact your license server for activation
            activation_data = {
                'license_key': license_key,
                'email': user_email,
                'machine_id': self.machine_id,
                'platform': platform.platform(),
                'app_version': '1.0.0'
            }
            
            # In production, this would contact your actual license server
            # For now, simulate server response
            response = self._simulate_license_server_response(activation_data)
            
            if response.get('success'):
                license_data = response['license_data']
                license_data['signature'] = self._create_license_signature(license_data)
                
                # Encrypt and save license
                encrypted_license = self._encrypt_data(json.dumps(license_data))
                with open(self.license_file, 'w') as f:
                    f.write(encrypted_license)
                
                return True, "License activated successfully"
            else:
                return False, response.get('error', 'License activation failed')
                
        except Exception as e:
            return False, f"Activation error: {str(e)}"
    
    def _simulate_license_server_response(self, activation_data: Dict) -> Dict:
        """Simulate license server response (replace with actual server call)"""
        # This is where you'd implement your actual license server logic
        # For demonstration, we'll create a valid response
        
        license_key = activation_data.get('license_key', '')
        
        # Example: Check if license key follows your format
        if len(license_key) >= 20 and license_key.startswith('VARSYS-'):
            return {
                'success': True,
                'license_data': {
                    'user_id': str(uuid.uuid4()),
                    'email': activation_data['email'],
                    'license_key': license_key,
                    'machine_id': activation_data['machine_id'],
                    'license_type': 'commercial',
                    'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),
                    'activated_at': datetime.now().isoformat(),
                    'features': ['full_access', 'firebase_sync', 'ai_insights', 'reports']
                }
            }
        else:
            return {
                'success': False,
                'error': 'Invalid license key format'
            }
    
    def verify_license(self) -> Tuple[bool, str, Optional[Dict]]:
        """Verify current license status"""
        try:
            # Check if license file exists
            if not os.path.exists(self.license_file):
                return False, "No license found. Please activate your license.", None
            
            # Read and decrypt license
            with open(self.license_file, 'r') as f:
                encrypted_license = f.read()
            
            license_json = self._decrypt_data(encrypted_license)
            license_data = json.loads(license_json)
            
            # Verify signature (tamper detection)
            if not self._verify_license_signature(license_data):
                return False, "License has been tampered with. Please contact support.", None
            
            # Verify machine ID
            if license_data.get('machine_id') != self.machine_id:
                return False, "License is not valid for this machine.", None
            
            # Check expiration
            expires_at = datetime.fromisoformat(license_data.get('expires_at', ''))
            if datetime.now() > expires_at:
                return False, "License has expired. Please renew your license.", None
            
            # Periodic online verification (every 7 days)
            last_online_check = license_data.get('last_online_check', '')
            if last_online_check:
                last_check = datetime.fromisoformat(last_online_check)
                if datetime.now() - last_check > timedelta(days=7):
                    online_valid, message = self._perform_online_verification(license_data)
                    if not online_valid:
                        return False, f"Online verification failed: {message}", None
                    
                    # Update last check time
                    license_data['last_online_check'] = datetime.now().isoformat()
                    license_data['signature'] = self._create_license_signature(license_data)
                    encrypted_license = self._encrypt_data(json.dumps(license_data))
                    with open(self.license_file, 'w') as f:
                        f.write(encrypted_license)
            
            return True, "License valid", license_data
            
        except Exception as e:
            return False, f"License verification error: {str(e)}", None
    
    def _perform_online_verification(self, license_data: Dict) -> Tuple[bool, str]:
        """Perform online license verification with your server"""
        try:
            verification_data = {
                'license_key': license_data.get('license_key'),
                'machine_id': self.machine_id,
                'user_id': license_data.get('user_id')
            }
            
            # In production, contact your license server
            # For now, simulate successful verification
            return True, "Online verification successful"
            
        except Exception as e:
            # If online verification fails, allow offline usage for limited time
            return True, f"Offline mode: {str(e)}"
    
    def get_license_info(self) -> Optional[Dict]:
        """Get current license information"""
        valid, message, license_data = self.verify_license()
        if valid and license_data:
            return {
                'email': license_data.get('email'),
                'license_type': license_data.get('license_type'),
                'expires_at': license_data.get('expires_at'),
                'features': license_data.get('features', []),
                'days_remaining': (datetime.fromisoformat(license_data.get('expires_at', '')) - datetime.now()).days
            }
        return None
    
    def deactivate_license(self) -> bool:
        """Deactivate current license"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            return True
        except Exception:
            return False
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if specific feature is enabled in license"""
        valid, _, license_data = self.verify_license()
        if valid and license_data:
            features = license_data.get('features', [])
            return feature in features or 'full_access' in features
        return False

# Global license manager instance
license_manager = LicenseManager()

def require_license(feature: str = 'full_access'):
    """Decorator to require valid license for functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not license_manager.is_feature_enabled(feature):
                raise PermissionError(f"Valid license required for {feature}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_license_on_startup() -> bool:
    """Check license when application starts"""
    valid, message, _ = license_manager.verify_license()
    if not valid:
        print(f"License Error: {message}")
        return False
    return True
