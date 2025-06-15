"""
Authentication dependencies for token validation
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from ..config import settings
from ..schemas import TokenPayload, CurrentUser
from ..services.jwks_service import jwks_service

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Dependency to get current authenticated user from JWT token
    
    This function:
    1. Extracts Bearer token from Authorization header
    2. Fetches JWKS from auth server to get public key
    3. Verifies token signature using public key
    4. Validates token expiration
    5. Extracts user information from token payload
    
    Args:
        credentials: HTTP authorization credentials containing the Bearer token
        
    Returns:
        CurrentUser: User information extracted from validated token
        
    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    
    # Extract token from credentials
    token = credentials.credentials
    
    try:
        # Decode token header to get key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Get public key for token verification
        if kid:
            public_key = jwks_service.get_public_key_by_kid(kid)
        else:
            # Fallback to default key if no kid specified
            public_key = jwks_service.get_default_public_key()
        
        if not public_key:
            logger.error("No public key available for token verification")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to verify token: no public key available",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify and decode JWT token
        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[settings.jwt_algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": False,  # We're not using audience validation
                    "verify_iss": False,  # We're not using issuer validation
                }
            )
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate token payload structure
        try:
            token_data = TokenPayload(**payload)
        except Exception as e:
            logger.error(f"Invalid token payload structure: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Additional expiration check (jose should handle this, but double-check)
        current_time = datetime.utcnow().timestamp()
        if token_data.exp < current_time:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user information from token
        try:
            user_id = int(token_data.sub)
        except (ValueError, TypeError):
            logger.error(f"Invalid user ID in token: {token_data.sub}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create and return current user object
        current_user = CurrentUser(
            id=user_id,
            group=token_data.group,
            department=token_data.department
        )
        
        logger.debug(f"Successfully authenticated user: {user_id}")
        return current_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Optional dependency to get current user (allows anonymous access)
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Optional[CurrentUser]: User information if token is valid, None if no token
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


def require_group(required_group: str):
    """
    Dependency factory to require specific user group
    
    Args:
        required_group: The group that the user must belong to
        
    Returns:
        Function that validates user group
    """
    def group_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.group != required_group:
            logger.warning(f"User {current_user.id} does not have required group: {required_group}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires '{required_group}' group"
            )
        return current_user
    
    return group_checker


def require_department(required_department: str):
    """
    Dependency factory to require specific user department
    
    Args:
        required_department: The department that the user must belong to
        
    Returns:
        Function that validates user department
    """
    def department_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.department != required_department:
            logger.warning(f"User {current_user.id} does not have required department: {required_department}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires '{required_department}' department"
            )
        return current_user
    
    return department_checker 