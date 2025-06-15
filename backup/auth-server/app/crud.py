"""
CRUD operations for database models
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from passlib.context import CryptContext

from .models import (
    User, Role, Group, Permission, Feature, ServiceCategory, Service, 
    Workspace, RefreshToken, user_permissions, user_features, 
    role_permissions, role_features, group_permissions, group_features,
    user_service_permissions
)
from .schemas import (
    UserCreate, UserUpdate, RoleCreate, RoleUpdate, GroupCreate, GroupUpdate,
    PermissionCreate, PermissionUpdate, FeatureCreate, FeatureUpdate,
    ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCreate, ServiceUpdate,
    WorkspaceCreate, WorkspaceUpdate
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

# ==================== USER CRUD ====================
def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None

def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """Get user by phone number"""
    try:
        return db.query(User).filter(User.phone_number == phone).first()
    except Exception as e:
        logger.error(f"Error getting user by phone {phone}: {e}")
        return None

def get_users(db: Session, skip: int = 0, limit: int = 100, 
              include_inactive: bool = False) -> List[User]:
    """Get users with pagination"""
    try:
        query = db.query(User)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return []

def get_users_by_role(db: Session, role_id: int) -> List[User]:
    """Get users by role"""
    try:
        return db.query(User).filter(User.role_id == role_id).all()
    except Exception as e:
        logger.error(f"Error getting users by role {role_id}: {e}")
        return []

def get_users_by_group(db: Session, group_id: int) -> List[User]:
    """Get users by group"""
    try:
        return db.query(User).filter(User.group_id == group_id).all()
    except Exception as e:
        logger.error(f"Error getting users by group {group_id}: {e}")
        return []

def get_users_by_department(db: Session, department: str) -> List[User]:
    """Get users by department"""
    try:
        return db.query(User).filter(User.department == department).all()
    except Exception as e:
        logger.error(f"Error getting users by department {department}: {e}")
        return []

def get_pending_users(db: Session) -> List[User]:
    """Get users pending approval"""
    try:
        return db.query(User).filter(User.approval_status == 'pending').all()
    except Exception as e:
        logger.error(f"Error getting pending users: {e}")
        return []

def create_user(db: Session, user: UserCreate, created_by: Optional[str] = None) -> User:
    """Create new user"""
    try:
        # Check if user exists
        if get_user_by_email(db, user.email):
            raise ValueError("User with this email already exists")
        
        if user.phone_number and get_user_by_phone(db, user.phone_number):
            raise ValueError("User with this phone number already exists")
        
        # Create user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            real_name=user.real_name,
            display_name=user.display_name or user.real_name,
            email=user.email,
            phone_number=user.phone_number,
            hashed_password=hashed_password,
            department=user.department,
            position=user.position,
            bio=user.bio,
            is_active=False,  # Pending approval
            approval_status='pending'
        )
        
        # Assign default role and group
        default_role = get_role_by_name(db, "user")
        if default_role:
            db_user.role_id = default_role.id
            
        default_group = get_group_by_name(db, "Default Users")
        if default_group:
            db_user.group_id = default_group.id
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Assign requested permissions and features
        if user.requested_permissions:
            for permission_id in user.requested_permissions:
                permission = get_permission(db, permission_id)
                if permission and permission.category == 'basic':
                    db_user.permissions.append(permission)
        
        if user.requested_features:
            for feature_id in user.requested_features:
                feature = get_feature(db, feature_id)
                if feature and feature.auto_grant:
                    db_user.features.append(feature)
        
        db.commit()
        logger.info(f"Created user: {db_user.email}")
        return db_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise

def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return None
            
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Updated user: {user_id}")
        return db_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        return None

def approve_user(db: Session, user_id: str, approved_by: str, 
                approval_status: str, approval_note: Optional[str] = None) -> Optional[User]:
    """Approve or reject user"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return None
            
        db_user.approval_status = approval_status
        db_user.approval_note = approval_note
        db_user.approved_by = approved_by
        db_user.approved_at = datetime.utcnow()
        db_user.is_active = approval_status == 'approved'
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User {user_id} {approval_status} by {approved_by}")
        return db_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving user {user_id}: {e}")
        return None

def delete_user(db: Session, user_id: str) -> bool:
    """Delete user"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return False
            
        db.delete(db_user)
        db.commit()
        
        logger.info(f"Deleted user: {user_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        return False

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user"""
    try:
        user = get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active or user.approval_status != 'approved':
            return None
            
        # Update login stats
        user.last_login_at = datetime.utcnow()
        user.login_count += 1
        db.commit()
        
        return user
        
    except Exception as e:
        logger.error(f"Error authenticating user {email}: {e}")
        return None

# ==================== ROLE CRUD ====================
def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Get role by ID"""
    try:
        return db.query(Role).filter(Role.id == role_id).first()
    except Exception as e:
        logger.error(f"Error getting role {role_id}: {e}")
        return None

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get role by name"""
    try:
        return db.query(Role).filter(Role.name == name).first()
    except Exception as e:
        logger.error(f"Error getting role by name {name}: {e}")
        return None

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """Get roles with pagination"""
    try:
        return db.query(Role).filter(Role.is_active == True).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting roles: {e}")
        return []

def create_role(db: Session, role: RoleCreate) -> Role:
    """Create new role"""
    try:
        if get_role_by_name(db, role.name):
            raise ValueError("Role with this name already exists")
            
        db_role = Role(
            name=role.name,
            description=role.description,
            is_active=role.is_active
        )
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        
        # Assign permissions and features
        if role.permission_ids:
            for permission_id in role.permission_ids:
                permission = get_permission(db, permission_id)
                if permission:
                    db_role.permissions.append(permission)
        
        if role.feature_ids:
            for feature_id in role.feature_ids:
                feature = get_feature(db, feature_id)
                if feature:
                    db_role.features.append(feature)
        
        db.commit()
        logger.info(f"Created role: {role.name}")
        return db_role
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating role: {e}")
        raise

def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    """Update role"""
    try:
        db_role = get_role(db, role_id)
        if not db_role:
            return None
            
        update_data = role_update.model_dump(exclude_unset=True)
        
        # Handle permissions and features separately
        permission_ids = update_data.pop('permission_ids', None)
        feature_ids = update_data.pop('feature_ids', None)
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        # Update permissions
        if permission_ids is not None:
            db_role.permissions.clear()
            for permission_id in permission_ids:
                permission = get_permission(db, permission_id)
                if permission:
                    db_role.permissions.append(permission)
        
        # Update features
        if feature_ids is not None:
            db_role.features.clear()
            for feature_id in feature_ids:
                feature = get_feature(db, feature_id)
                if feature:
                    db_role.features.append(feature)
        
        db.commit()
        db.refresh(db_role)
        
        logger.info(f"Updated role: {role_id}")
        return db_role
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating role {role_id}: {e}")
        return None

def delete_role(db: Session, role_id: int) -> bool:
    """Delete role"""
    try:
        db_role = get_role(db, role_id)
        if not db_role:
            return False
            
        # Check if role is in use
        users_count = db.query(User).filter(User.role_id == role_id).count()
        if users_count > 0:
            raise ValueError(f"Cannot delete role: {users_count} users are assigned to this role")
            
        db.delete(db_role)
        db.commit()
        
        logger.info(f"Deleted role: {role_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting role {role_id}: {e}")
        return False

# ==================== GROUP CRUD ====================
def get_group(db: Session, group_id: int) -> Optional[Group]:
    """Get group by ID"""
    try:
        return db.query(Group).filter(Group.id == group_id).first()
    except Exception as e:
        logger.error(f"Error getting group {group_id}: {e}")
        return None

def get_group_by_name(db: Session, name: str) -> Optional[Group]:
    """Get group by name"""
    try:
        return db.query(Group).filter(Group.name == name).first()
    except Exception as e:
        logger.error(f"Error getting group by name {name}: {e}")
        return None

def get_groups(db: Session, skip: int = 0, limit: int = 100) -> List[Group]:
    """Get groups with pagination"""
    try:
        return db.query(Group).filter(Group.is_active == True).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting groups: {e}")
        return []

def create_group(db: Session, group: GroupCreate, created_by: str) -> Group:
    """Create new group"""
    try:
        if get_group_by_name(db, group.name):
            raise ValueError("Group with this name already exists")
            
        db_group = Group(
            name=group.name,
            description=group.description,
            is_active=group.is_active,
            created_by=created_by
        )
        
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        
        # Assign permissions and features
        if group.permission_ids:
            for permission_id in group.permission_ids:
                permission = get_permission(db, permission_id)
                if permission:
                    db_group.permissions.append(permission)
        
        if group.feature_ids:
            for feature_id in group.feature_ids:
                feature = get_feature(db, feature_id)
                if feature:
                    db_group.features.append(feature)
        
        db.commit()
        logger.info(f"Created group: {group.name}")
        return db_group
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating group: {e}")
        raise

# ==================== PERMISSION CRUD ====================
def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    """Get permission by ID"""
    try:
        return db.query(Permission).filter(Permission.id == permission_id).first()
    except Exception as e:
        logger.error(f"Error getting permission {permission_id}: {e}")
        return None

def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    """Get permission by name"""
    try:
        return db.query(Permission).filter(Permission.name == name).first()
    except Exception as e:
        logger.error(f"Error getting permission by name {name}: {e}")
        return None

def get_permissions(db: Session, category: Optional[str] = None) -> List[Permission]:
    """Get permissions by category"""
    try:
        query = db.query(Permission).filter(Permission.is_active == True)
        if category:
            query = query.filter(Permission.category == category)
        return query.all()
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        return []

def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    """Create new permission"""
    try:
        if get_permission_by_name(db, permission.name):
            raise ValueError("Permission with this name already exists")
            
        db_permission = Permission(**permission.model_dump())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        
        logger.info(f"Created permission: {permission.name}")
        return db_permission
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating permission: {e}")
        raise

# ==================== FEATURE CRUD ====================
def get_feature(db: Session, feature_id: int) -> Optional[Feature]:
    """Get feature by ID"""
    try:
        return db.query(Feature).filter(Feature.id == feature_id).first()
    except Exception as e:
        logger.error(f"Error getting feature {feature_id}: {e}")
        return None

def get_feature_by_name(db: Session, name: str) -> Optional[Feature]:
    """Get feature by name"""
    try:
        return db.query(Feature).filter(Feature.name == name).first()
    except Exception as e:
        logger.error(f"Error getting feature by name {name}: {e}")
        return None

def get_features(db: Session, category: Optional[str] = None) -> List[Feature]:
    """Get features by category"""
    try:
        query = db.query(Feature).filter(Feature.is_active == True)
        if category:
            query = query.filter(Feature.category == category)
        return query.order_by(Feature.category, Feature.display_name).all()
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        return []

def create_feature(db: Session, feature: FeatureCreate) -> Feature:
    """Create new feature"""
    try:
        if get_feature_by_name(db, feature.name):
            raise ValueError("Feature with this name already exists")
            
        db_feature = Feature(**feature.model_dump())
        db.add(db_feature)
        db.commit()
        db.refresh(db_feature)
        
        logger.info(f"Created feature: {feature.name}")
        return db_feature
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating feature: {e}")
        raise

# ==================== SERVICE CRUD ====================
def get_service_category(db: Session, category_id: int) -> Optional[ServiceCategory]:
    """Get service category by ID"""
    try:
        return db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    except Exception as e:
        logger.error(f"Error getting service category {category_id}: {e}")
        return None

def get_service_categories(db: Session) -> List[ServiceCategory]:
    """Get all service categories"""
    try:
        return db.query(ServiceCategory).filter(ServiceCategory.is_active == True)\
                                        .order_by(ServiceCategory.sort_order).all()
    except Exception as e:
        logger.error(f"Error getting service categories: {e}")
        return []

def get_service(db: Session, service_id: int) -> Optional[Service]:
    """Get service by ID"""
    try:
        return db.query(Service).filter(Service.id == service_id).first()
    except Exception as e:
        logger.error(f"Error getting service {service_id}: {e}")
        return None

def get_services(db: Session, category_id: Optional[int] = None) -> List[Service]:
    """Get services by category"""
    try:
        query = db.query(Service).filter(Service.is_active == True)
        if category_id:
            query = query.filter(Service.category_id == category_id)
        return query.order_by(Service.sort_order).all()
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        return []

def create_service(db: Session, service: ServiceCreate, created_by: str) -> Service:
    """Create new service"""
    try:
        db_service = Service(
            **service.model_dump(),
            created_by=created_by
        )
        
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        
        logger.info(f"Created service: {service.name}")
        return db_service
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating service: {e}")
        raise

# ==================== WORKSPACE CRUD ====================
def get_workspace(db: Session, workspace_id: int) -> Optional[Workspace]:
    """Get workspace by ID"""
    try:
        return db.query(Workspace).filter(Workspace.id == workspace_id).first()
    except Exception as e:
        logger.error(f"Error getting workspace {workspace_id}: {e}")
        return None

def get_user_workspaces(db: Session, user_id: str) -> List[Workspace]:
    """Get workspaces for user"""
    try:
        return db.query(Workspace).filter(
            Workspace.owner_id == user_id,
            Workspace.is_active == True
        ).order_by(desc(Workspace.updated_at)).all()
    except Exception as e:
        logger.error(f"Error getting workspaces for user {user_id}: {e}")
        return []

def create_workspace(db: Session, workspace: WorkspaceCreate, owner_id: str) -> Workspace:
    """Create new workspace"""
    try:
        db_workspace = Workspace(
            **workspace.model_dump(),
            owner_id=owner_id
        )
        
        db.add(db_workspace)
        db.commit()
        db.refresh(db_workspace)
        
        logger.info(f"Created workspace: {workspace.name} for user {owner_id}")
        return db_workspace
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating workspace: {e}")
        raise

# ==================== REFRESH TOKEN CRUD ====================
def create_refresh_token(db: Session, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
    """Create refresh token"""
    try:
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        
        return db_token
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating refresh token: {e}")
        raise

def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Get refresh token"""
    try:
        return db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
    except Exception as e:
        logger.error(f"Error getting refresh token: {e}")
        return None

def revoke_refresh_token(db: Session, token: str, replaced_by: Optional[str] = None) -> bool:
    """Revoke refresh token"""
    try:
        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if not db_token:
            return False
            
        db_token.revoked = True
        if replaced_by:
            db_token.replaced_by_token = replaced_by
            
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking refresh token: {e}")
        return False

def revoke_user_tokens(db: Session, user_id: str) -> bool:
    """Revoke all user refresh tokens"""
    try:
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id)\
                              .update({RefreshToken.revoked: True})
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking user tokens: {e}")
        return False

# ==================== STATISTICS ====================
def get_system_stats(db: Session) -> Dict[str, Any]:
    """Get system statistics"""
    try:
        return {
            "total_users": db.query(User).count(),
            "active_users": db.query(User).filter(User.is_active == True).count(),
            "pending_approvals": db.query(User).filter(User.approval_status == 'pending').count(),
            "total_workspaces": db.query(Workspace).count(),
            "active_services": db.query(Service).filter(Service.is_active == True).count(),
            "system_health": "healthy"
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {}

def get_user_stats(db: Session, user_id: str) -> Dict[str, Any]:
    """Get user statistics"""
    try:
        user = get_user(db, user_id)
        if not user:
            return {}
            
        workspace_count = db.query(Workspace).filter(
            Workspace.owner_id == user_id,
            Workspace.is_active == True
        ).count()
        
        active_features = len(user.features)
        
        return {
            "user_id": user_id,
            "login_count": user.login_count,
            "last_login_at": user.last_login_at,
            "workspace_count": workspace_count,
            "active_features": active_features
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return {}

# Convenience instances
user_crud = UserCRUD()
refresh_token_crud = RefreshTokenCRUD() 