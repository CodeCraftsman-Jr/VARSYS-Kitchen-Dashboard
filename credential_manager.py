"""
Credential Manager for Kitchen Dashboard

This module provides secure handling of Firebase credentials
by encrypting them with a machine-specific key.
"""

import os
import json
import base64
import tempfile
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages secure access to Firebase credentials"""
    
    def __init__(self, app_id="KitchenDashboard-v2.0.0"):
        """Initialize the credential manager with a unique app ID."""
        self.app_id = app_id
        self._key = self._derive_key()
        self.fernet = Fernet(self._key)
        self.temp_files = []
        
    def _derive_key(self):
        """Derive a key based on machine-specific information and app ID."""
        # Use a combination of machine-specific information
        salt = (os.getenv('COMPUTERNAME', '') + self.app_id).encode()
        
        # Use PBKDF2 to derive a secure key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Generate key from machine-specific information
        base_info = (
            os.getenv('USERNAME', '') + 
            os.getenv('COMPUTERNAME', '') + 
            self.app_id
        ).encode()
        
        key = base64.urlsafe_b64encode(kdf.derive(base_info))
        return key
    
    def get_credentials_path(self):
        """Get the path to the Firebase credentials file."""
        # First check if the credentials file exists in the current directory
        creds_path = os.path.join(os.path.dirname(__file__), "firebase_credentials.json")
        if os.path.exists(creds_path):
            return creds_path
            
        # If not, check in the executable's directory
        exe_dir = os.path.dirname(sys.executable)
        creds_path = os.path.join(exe_dir, "firebase_credentials.json")
        if os.path.exists(creds_path):
            return creds_path
            
        # If still not found, return None
        logger.warning("Firebase credentials file not found")
        return None
        
    def get_web_config_path(self):
        """Get the path to the Firebase web config file."""
        # First check if the web config file exists in the current directory
        config_path = os.path.join(os.path.dirname(__file__), "firebase_web_config.json")
        if os.path.exists(config_path):
            return config_path
            
        # If not, check in the executable's directory
        exe_dir = os.path.dirname(sys.executable)
        config_path = os.path.join(exe_dir, "firebase_web_config.json")
        if os.path.exists(config_path):
            return config_path
            
        # If still not found, return None
        logger.warning("Firebase web config file not found")
        return None
    
    def encrypt_file(self, file_path):
        """Encrypt a file and return the encrypted data."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.fernet.encrypt(data)
            return encrypted_data
        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {e}")
            return None
    
    def decrypt_to_temp_file(self, encrypted_data, prefix="firebase_", suffix=".json"):
        """Decrypt data and save it to a temporary file."""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            with os.fdopen(fd, 'wb') as f:
                f.write(decrypted_data)
            
            # Add to list of temp files to clean up later
            self.temp_files.append(temp_path)
            
            return temp_path
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.error(f"Error removing temp file {temp_file}: {e}")
        
        self.temp_files = []

# Helper function to encrypt credentials for distribution
def encrypt_credentials():
    """Encrypt the Firebase credentials for distribution."""
    manager = CredentialManager()
    
    # Get paths to credential files
    creds_path = os.path.join(os.path.dirname(__file__), "firebase_credentials.json")
    config_path = os.path.join(os.path.dirname(__file__), "firebase_web_config.json")
    
    # Encrypt the files
    encrypted_creds = manager.encrypt_file(creds_path)
    encrypted_config = manager.encrypt_file(config_path)
    
    # Save the encrypted files
    with open(creds_path + ".enc", 'wb') as f:
        f.write(encrypted_creds)
    
    with open(config_path + ".enc", 'wb') as f:
        f.write(encrypted_config)
    
    print(f"Credentials encrypted and saved to {creds_path}.enc and {config_path}.enc")

if __name__ == "__main__":
    # If run directly, encrypt the credentials
    encrypt_credentials()
