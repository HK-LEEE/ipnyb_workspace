"""
Security utilities for JWT handling and password management
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import base64

from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .config import settings
from .schemas import TokenPayload

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Manages JWT tokens and security operations"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.load_or_generate_keys()
    
    def load_or_generate_keys(self):
        """Load existing RSA keys or generate new ones"""
        try:
            # Ensure keys directory exists
            os.makedirs(os.path.dirname(settings.jwt_private_key_path), exist_ok=True)
            
            # Try to load existing keys
            if os.path.exists(settings.jwt_private_key_path) and os.path.exists(settings.jwt_public_key_path):
                self.load_keys()
            else:
                self.generate_keys()
                
        except Exception as e:
            logger.error(f"Failed to initialize RSA keys: {e}")
            raise
    
    def generate_keys(self):
        """Generate new RSA key pair"""
        logger.info("Generating new RSA key pair...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save keys to files
        with open(settings.jwt_private_key_path, 'wb') as f:
            f.write(private_pem)
        
        with open(settings.jwt_public_key_path, 'wb') as f:
            f.write(public_pem)
        
        # Set permissions (Unix-like systems only)
        try:
            os.chmod(settings.jwt_private_key_path, 0o600)
            os.chmod(settings.jwt_public_key_path, 0o644)
        except:
            pass  # Windows doesn't support chmod
        
        self.private_key = private_pem.decode('utf-8')
        self.public_key = public_pem.decode('utf-8')
        
        logger.info("RSA key pair generated successfully")
    
    def load_keys(self):
        """Load existing RSA keys from files"""
        try:
            with open(settings.jwt_private_key_path, 'r') as f:
                self.private_key = f.read()
            
            with open(settings.jwt_public_key_path, 'r') as f:
                self.public_key = f.read()
            
            logger.info("RSA keys loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load RSA keys: {e}")
            raise
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        try:
            now = datetime.utcnow()
            expire = now + timedelta(minutes=settings.access_token_expire_minutes)
            
            payload = {
                "sub": str(user_data["id"]),
                "exp": expire,
                "iat": now,
                "jti": str(uuid.uuid4()),
                "group": user_data.get("group"),
                "department": user_data.get("department")
            }
            
            token = jwt.encode(payload, self.private_key, algorithm=settings.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    def create_refresh_token(self) -> str:
        """Create a secure refresh token"""
        return str(uuid.uuid4())
    
    def hash_refresh_token(self, token: str) -> str:
        """Hash refresh token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def verify_access_token(self, token: str) -> Optional[TokenPayload]:
        """Verify and decode JWT access token"""
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[settings.jwt_algorithm])
            token_data = TokenPayload(**payload)
            return token_data
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set for token verification"""
        try:
            # Load public key
            from cryptography.hazmat.primitives import serialization
            
            public_key_obj = serialization.load_pem_public_key(
                self.public_key.encode('utf-8'),
                backend=default_backend()
            )
            
            # Get key components
            public_numbers = public_key_obj.public_numbers()
            
            # Convert to base64url format
            def int_to_base64url(value: int) -> str:
                byte_length = (value.bit_length() + 7) // 8
                value_bytes = value.to_bytes(byte_length, byteorder='big')
                return base64.urlsafe_b64encode(value_bytes).decode('utf-8').rstrip('=')
            
            n = int_to_base64url(public_numbers.n)
            e = int_to_base64url(public_numbers.e)
            
            jwks = {
                "keys": [
                    {
                        "kty": "RSA",
                        "use": "sig",
                        "kid": "auth-server-key-1",
                        "alg": settings.jwt_algorithm,
                        "n": n,
                        "e": e
                    }
                ]
            }
            
            return jwks
            
        except Exception as e:
            logger.error(f"Failed to generate JWKS: {e}")
            raise


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


# Global security manager instance
security_manager = SecurityManager() 