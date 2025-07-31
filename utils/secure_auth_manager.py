"""
Secure Authentication Manager
Handles secure authentication and credential management
"""

import os
import logging
from typing import Dict, Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SecureAuthManager:
    """Manages secure authentication and credential storage"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = '.encryption_key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_credential(self, credential: str) -> str:
        """Encrypt a credential"""
        return self.cipher.encrypt(credential.encode()).decode()
    
    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt a credential"""
        return self.cipher.decrypt(encrypted_credential.encode()).decode()
    
    def store_secure_credential(self, key: str, value: str) -> bool:
        """Store a credential securely"""
        try:
            encrypted_value = self.encrypt_credential(value)
            # In production, this would use a secure key-value store
            os.environ[f"SECURE_{key}"] = encrypted_value
            return True
        except Exception as e:
            logger.error(f"Failed to store credential {key}: {e}")
            return False
    
    def retrieve_secure_credential(self, key: str) -> Optional[str]:
        """Retrieve a credential securely"""
        try:
            encrypted_value = os.environ.get(f"SECURE_{key}")
            if encrypted_value:
                return self.decrypt_credential(encrypted_value)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve credential {key}: {e}")
            return None
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate all required credentials are present"""
        required_creds = [
            'KITE_API_KEY', 'KITE_ACCESS_TOKEN', 
            'TELEGRAM_BOT_TOKEN', 'TELEGRAM_ID'
        ]
        
        validation_results = {}
        for cred in required_creds:
            value = os.environ.get(cred)
            validation_results[cred] = bool(value and len(value) > 5)
            
        return validation_results

# Global instance
secure_auth_manager = SecureAuthManager()