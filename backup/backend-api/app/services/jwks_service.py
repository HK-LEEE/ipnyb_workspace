"""
JWKS (JSON Web Key Set) service for fetching and caching public keys
"""

import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from ..config import settings
from ..schemas import JWKSResponse, JWKSKey

logger = logging.getLogger(__name__)


class JWKSService:
    """Service for managing JWKS (JSON Web Key Set)"""
    
    def __init__(self):
        self.jwks_cache: Optional[Dict[str, Any]] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = timedelta(minutes=settings.jwks_cache_ttl_minutes)
    
    def _is_cache_valid(self) -> bool:
        """Check if JWKS cache is still valid"""
        if not self.jwks_cache or not self.cache_timestamp:
            return False
        
        return datetime.utcnow() - self.cache_timestamp < self.cache_ttl
    
    def _fetch_jwks_from_server(self) -> Optional[Dict[str, Any]]:
        """Fetch JWKS from auth server"""
        try:
            logger.info(f"Fetching JWKS from {settings.jwks_url}")
            
            response = requests.get(
                settings.jwks_url,
                timeout=10,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            jwks_data = response.json()
            logger.info("Successfully fetched JWKS from auth server")
            return jwks_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JWKS from auth server: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching JWKS: {e}")
            return None
    
    def get_jwks(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Get JWKS with caching"""
        # Return cached version if valid and not forcing refresh
        if not force_refresh and self._is_cache_valid():
            logger.debug("Returning cached JWKS")
            return self.jwks_cache
        
        # Fetch fresh JWKS
        fresh_jwks = self._fetch_jwks_from_server()
        if fresh_jwks:
            self.jwks_cache = fresh_jwks
            self.cache_timestamp = datetime.utcnow()
            logger.info("JWKS cache updated")
            return fresh_jwks
        
        # If fetch failed and we have cached data, return it
        if self.jwks_cache:
            logger.warning("Using expired JWKS cache due to fetch failure")
            return self.jwks_cache
        
        logger.error("No JWKS available (fetch failed and no cache)")
        return None
    
    def get_public_key_by_kid(self, kid: str) -> Optional[str]:
        """Get public key by Key ID"""
        jwks = self.get_jwks()
        if not jwks or "keys" not in jwks:
            logger.error("No JWKS available")
            return None
        
        # Find key by kid
        for key_data in jwks["keys"]:
            if key_data.get("kid") == kid:
                try:
                    # Convert JWK to PEM format
                    return self._jwk_to_pem(key_data)
                except Exception as e:
                    logger.error(f"Failed to convert JWK to PEM: {e}")
                    return None
        
        logger.warning(f"Public key with kid '{kid}' not found in JWKS")
        return None
    
    def get_default_public_key(self) -> Optional[str]:
        """Get the first available public key"""
        jwks = self.get_jwks()
        if not jwks or "keys" not in jwks or not jwks["keys"]:
            logger.error("No JWKS keys available")
            return None
        
        try:
            # Return the first key
            first_key = jwks["keys"][0]
            return self._jwk_to_pem(first_key)
        except Exception as e:
            logger.error(f"Failed to get default public key: {e}")
            return None
    
    def _jwk_to_pem(self, jwk_data: Dict[str, Any]) -> str:
        """Convert JWK to PEM format"""
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            import base64
            
            # Extract modulus and exponent
            n_bytes = base64.urlsafe_b64decode(jwk_data["n"] + "===")  # Add padding
            e_bytes = base64.urlsafe_b64decode(jwk_data["e"] + "===")  # Add padding
            
            # Convert to integers
            n = int.from_bytes(n_bytes, byteorder='big')
            e = int.from_bytes(e_bytes, byteorder='big')
            
            # Create RSA public key
            public_numbers = rsa.RSAPublicNumbers(e, n)
            public_key = public_numbers.public_key(backend=default_backend())
            
            # Convert to PEM format
            pem_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return pem_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to convert JWK to PEM: {e}")
            raise
    
    def refresh_cache(self) -> bool:
        """Force refresh JWKS cache"""
        logger.info("Force refreshing JWKS cache")
        fresh_jwks = self.get_jwks(force_refresh=True)
        return fresh_jwks is not None
    
    def clear_cache(self):
        """Clear JWKS cache"""
        logger.info("Clearing JWKS cache")
        self.jwks_cache = None
        self.cache_timestamp = None


# Global JWKS service instance
jwks_service = JWKSService() 