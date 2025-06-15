"""
Authentication router with comprehensive user management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..security import SecurityManager
from ..middleware import check_rate_limit
from ..schemas import (
    UserCreate, UserLogin, UserResponse, UserWithRelations, Token,
    PasswordReset, PasswordChange, UserApproval, UserUpdate,
    RoleResponse, GroupResponse, PermissionResponse, FeatureResponse
)
from ..crud import (
    get_user, get_user_by_email, create_user, authenticate_user,
    approve_user, update_user, get_users, get_pending_users,
    get_users_by_role, get_users_by_group, get_users_by_department,
    create_refresh_token, get_refresh_token, revoke_refresh_token,
    revoke_user_tokens
)
from ..models import User

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes={
        "read": "Read access",
        "write": "Write access", 
        "admin": "Admin access"
    }
)

# Security manager
security_manager = SecurityManager()

# Dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = security_manager.verify_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Get user from database
        user = get_user(db, user_id)
        if user is None:
            raise credentials_exception
            
        if not user.is_active or user.approval_status != 'approved':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive or not approved"
            )
            
        return user
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise credentials_exception

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# ==================== AUTHENTICATION ENDPOINTS ====================

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user (pending approval)"""
    try:
        # Validate phone number format if provided
        if user_data.phone_number and not validate_phone_number(user_data.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format. Use format: 010-1234-5678"
            )
        
        # Create user
        user = create_user(db, user_data)
        
        logger.info(f"User registered: {user.email} (pending approval)")
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Login user and return tokens"""
    
    # Rate limiting
    await check_rate_limit(request, "login")
    
    try:
        # Authenticate user
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
            
        if user.approval_status != 'approved':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is pending approval"
            )
        
        # Create tokens
        access_token = security_manager.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.name if user.role else "user",
                "department": user.department,
                "is_admin": user.is_admin
            }
        )
        
        refresh_token = security_manager.create_refresh_token(str(user.id))
        
        # Store refresh token in database
        expires_at = datetime.utcnow() + timedelta(days=7)
        create_refresh_token(db, str(user.id), refresh_token, expires_at)
        
        # Set refresh token as HttpOnly cookie
        if response:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7 days
                httponly=True,
                secure=True,
                samesite="strict"
            )
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Get refresh token from cookie or request body
        refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            # Try to get from request body as fallback
            body = await request.json()
            refresh_token = body.get("refresh_token")
            
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found"
            )
        
        # Verify refresh token
        payload = security_manager.verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        
        # Check if token exists in database and is not revoked
        db_token = get_refresh_token(db, refresh_token)
        if not db_token or db_token.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = get_user(db, user_id)
        if not user or not user.is_active or user.approval_status != 'approved':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens (refresh token rotation)
        new_access_token = security_manager.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.name if user.role else "user",
                "department": user.department,
                "is_admin": user.is_admin
            }
        )
        
        new_refresh_token = security_manager.create_refresh_token(str(user.id))
        
        # Revoke old refresh token and create new one
        revoke_refresh_token(db, refresh_token, new_refresh_token)
        expires_at = datetime.utcnow() + timedelta(days=7)
        create_refresh_token(db, str(user.id), new_refresh_token, expires_at)
        
        # Set new refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=True,
            samesite="strict"
        )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and revoke all tokens"""
    try:
        # Revoke all refresh tokens for the user
        revoke_user_tokens(db, str(current_user.id))
        
        # Clear refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="strict"
        )
        
        logger.info(f"User logged out: {current_user.email}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# ==================== USER PROFILE ENDPOINTS ====================

@router.get("/me", response_model=UserWithRelations)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with relationships"""
    try:
        # Get user with relationships loaded
        user = db.query(User).filter(User.id == current_user.id).first()
        
        return user
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    try:
        # Users can only update their own basic info
        allowed_fields = {
            'real_name', 'display_name', 'phone_number', 
            'department', 'position', 'bio'
        }
        
        update_data = user_update.model_dump(exclude_unset=True)
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Apply updates
        for field, value in filtered_data.items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.email}")
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        from ..crud import verify_password, get_password_hash
        
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        
        # Revoke all refresh tokens to force re-login
        revoke_user_tokens(db, str(current_user.id))
        
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully. Please login again."}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/users", response_model=List[UserWithRelations])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    role_id: Optional[int] = None,
    group_id: Optional[int] = None,
    department: Optional[str] = None,
    approval_status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        if role_id:
            users = get_users_by_role(db, role_id)
        elif group_id:
            users = get_users_by_group(db, group_id)
        elif department:
            users = get_users_by_department(db, department)
        else:
            users = get_users(db, skip, limit, include_inactive)
        
        # Filter by approval status if specified
        if approval_status:
            users = [u for u in users if u.approval_status == approval_status]
        
        return users
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/admin/users/pending", response_model=List[UserResponse])
async def get_pending_user_approvals(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get users pending approval (admin only)"""
    try:
        pending_users = get_pending_users(db)
        return pending_users
        
    except Exception as e:
        logger.error(f"Get pending users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending users"
        )

@router.put("/admin/users/{user_id}/approve", response_model=UserResponse)
async def approve_user_registration(
    user_id: UUID,
    approval_data: UserApproval,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Approve or reject user registration (admin only)"""
    try:
        if approval_data.approval_status not in ['approved', 'rejected']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid approval status. Must be 'approved' or 'rejected'"
            )
        
        user = approve_user(
            db, 
            str(user_id), 
            str(current_user.id),
            approval_data.approval_status,
            approval_data.approval_note
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User {user_id} {approval_data.approval_status} by {current_user.email}")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User approval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User approval failed"
        )

@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    try:
        user = update_user(db, str(user_id), user_update)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User {user_id} updated by admin {current_user.email}")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

# ==================== UTILITY FUNCTIONS ====================

def validate_phone_number(phone: str) -> bool:
    """Validate Korean phone number format"""
    import re
    pattern = r'^01[016789]-?\d{3,4}-?\d{4}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

# ==================== JWKS ENDPOINT ====================

@router.get("/.well-known/jwks.json")
async def get_jwks():
    """Get JSON Web Key Set for token verification"""
    try:
        return security_manager.get_jwks()
    except Exception as e:
        logger.error(f"JWKS error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get JWKS"
        ) 