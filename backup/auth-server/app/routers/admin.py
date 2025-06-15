"""
Administrative router for system management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..database import get_db
from ..schemas import (
    UserResponse, UserWithRelations, UserUpdate, UserApproval,
    RoleCreate, RoleUpdate, RoleResponse, RoleWithRelations,
    GroupCreate, GroupUpdate, GroupResponse, GroupWithRelations,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    FeatureCreate, FeatureUpdate, FeatureResponse,
    ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryResponse,
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceWithCategory,
    WorkspaceResponse, WorkspaceWithOwner,
    SystemStats, UserStats, BulkPermissionUpdate, BulkFeatureUpdate
)
from ..crud import (
    # User CRUD
    get_user, get_users, get_pending_users, get_users_by_role,
    get_users_by_group, get_users_by_department, update_user,
    approve_user, delete_user,
    
    # Role CRUD
    get_role, get_roles, create_role, update_role, delete_role,
    get_role_by_name,
    
    # Group CRUD
    get_group, get_groups, create_group, get_group_by_name,
    
    # Permission CRUD
    get_permission, get_permissions, create_permission,
    get_permission_by_name,
    
    # Feature CRUD
    get_feature, get_features, create_feature, get_feature_by_name,
    
    # Service CRUD
    get_service_category, get_service_categories, get_service,
    get_services, create_service,
    
    # Workspace CRUD
    get_workspace, get_user_workspaces,
    
    # Statistics
    get_system_stats, get_user_stats
)
from ..models import User, Role, Group, Permission, Feature, Service, Workspace
from .auth import get_current_admin_user

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== USER MANAGEMENT ====================

@router.get("/users", response_model=List[UserWithRelations])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_inactive: bool = Query(False),
    role_id: Optional[int] = Query(None),
    group_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    approval_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with filtering options"""
    try:
        if role_id:
            users = get_users_by_role(db, role_id)
        elif group_id:
            users = get_users_by_group(db, group_id)
        elif department:
            users = get_users_by_department(db, department)
        else:
            users = get_users(db, skip, limit, include_inactive)
        
        # Apply additional filters
        if approval_status:
            users = [u for u in users if u.approval_status == approval_status]
        
        if search:
            search_lower = search.lower()
            users = [u for u in users if 
                    search_lower in u.real_name.lower() or
                    search_lower in (u.display_name or "").lower() or
                    search_lower in u.email.lower() or
                    search_lower in (u.department or "").lower()]
        
        return users
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users_admin(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get users pending approval"""
    try:
        pending_users = get_pending_users(db)
        return pending_users
        
    except Exception as e:
        logger.error(f"Get pending users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending users"
        )

@router.get("/users/{user_id}", response_model=UserWithRelations)
async def get_user_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get specific user details"""
    try:
        user = get_user(db, str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (admin can update all fields)"""
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

@router.put("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user_admin(
    user_id: UUID,
    approval_data: UserApproval,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Approve or reject user registration"""
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

@router.delete("/users/{user_id}")
async def delete_user_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user"""
    try:
        # Prevent admin from deleting themselves
        if str(user_id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = delete_user(db, str(user_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User {user_id} deleted by admin {current_user.email}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )

# ==================== ROLE MANAGEMENT ====================

@router.get("/roles", response_model=List[RoleWithRelations])
async def get_all_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    try:
        roles = get_roles(db, skip, limit)
        return roles
        
    except Exception as e:
        logger.error(f"Get roles error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get roles"
        )

@router.post("/roles", response_model=RoleResponse)
async def create_role_admin(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new role"""
    try:
        role = create_role(db, role_data)
        
        logger.info(f"Role '{role.name}' created by admin {current_user.email}")
        return role
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create role error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role creation failed"
        )

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role_admin(
    role_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update role"""
    try:
        role = update_role(db, role_id, role_update)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        logger.info(f"Role {role_id} updated by admin {current_user.email}")
        return role
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update role error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role update failed"
        )

@router.delete("/roles/{role_id}")
async def delete_role_admin(
    role_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete role"""
    try:
        success = delete_role(db, role_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        logger.info(f"Role {role_id} deleted by admin {current_user.email}")
        return {"message": "Role deleted successfully"}
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Delete role error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role deletion failed"
        )

# ==================== GROUP MANAGEMENT ====================

@router.get("/groups", response_model=List[GroupWithRelations])
async def get_all_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all groups"""
    try:
        groups = get_groups(db, skip, limit)
        return groups
        
    except Exception as e:
        logger.error(f"Get groups error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get groups"
        )

@router.post("/groups", response_model=GroupResponse)
async def create_group_admin(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new group"""
    try:
        group = create_group(db, group_data, str(current_user.id))
        
        logger.info(f"Group '{group.name}' created by admin {current_user.email}")
        return group
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create group error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Group creation failed"
        )

# ==================== PERMISSION MANAGEMENT ====================

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all permissions"""
    try:
        permissions = get_permissions(db, category)
        return permissions
        
    except Exception as e:
        logger.error(f"Get permissions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get permissions"
        )

@router.post("/permissions", response_model=PermissionResponse)
async def create_permission_admin(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new permission"""
    try:
        permission = create_permission(db, permission_data)
        
        logger.info(f"Permission '{permission.name}' created by admin {current_user.email}")
        return permission
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create permission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission creation failed"
        )

# ==================== FEATURE MANAGEMENT ====================

@router.get("/features", response_model=List[FeatureResponse])
async def get_all_features(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all features"""
    try:
        features = get_features(db, category)
        return features
        
    except Exception as e:
        logger.error(f"Get features error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get features"
        )

@router.post("/features", response_model=FeatureResponse)
async def create_feature_admin(
    feature_data: FeatureCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new feature"""
    try:
        feature = create_feature(db, feature_data)
        
        logger.info(f"Feature '{feature.name}' created by admin {current_user.email}")
        return feature
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create feature error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Feature creation failed"
        )

# ==================== SERVICE MANAGEMENT ====================

@router.get("/service-categories", response_model=List[ServiceCategoryResponse])
async def get_service_categories_admin(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all service categories"""
    try:
        categories = get_service_categories(db)
        return categories
        
    except Exception as e:
        logger.error(f"Get service categories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service categories"
        )

@router.get("/services", response_model=List[ServiceWithCategory])
async def get_services_admin(
    category_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all services"""
    try:
        services = get_services(db, category_id)
        return services
        
    except Exception as e:
        logger.error(f"Get services error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get services"
        )

@router.post("/services", response_model=ServiceResponse)
async def create_service_admin(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new service"""
    try:
        service = create_service(db, service_data, str(current_user.id))
        
        logger.info(f"Service '{service.name}' created by admin {current_user.email}")
        return service
        
    except Exception as e:
        logger.error(f"Create service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service creation failed"
        )

# ==================== WORKSPACE MANAGEMENT ====================

@router.get("/workspaces", response_model=List[WorkspaceWithOwner])
async def get_all_workspaces(
    user_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all workspaces"""
    try:
        if user_id:
            workspaces = get_user_workspaces(db, str(user_id))
        else:
            # Get all workspaces
            workspaces = db.query(Workspace).all()
        
        return workspaces
        
    except Exception as e:
        logger.error(f"Get workspaces error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workspaces"
        )

# ==================== SYSTEM STATISTICS ====================

@router.get("/stats/system", response_model=SystemStats)
async def get_system_statistics(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics"""
    try:
        stats = get_system_stats(db)
        return stats
        
    except Exception as e:
        logger.error(f"Get system stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system statistics"
        )

@router.get("/stats/users/{user_id}", response_model=UserStats)
async def get_user_statistics(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    try:
        stats = get_user_stats(db, str(user_id))
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )

# ==================== BULK OPERATIONS ====================

@router.post("/users/permissions/bulk")
async def bulk_update_user_permissions(
    bulk_update: BulkPermissionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk grant or revoke permissions for multiple users"""
    try:
        if bulk_update.action not in ['grant', 'revoke']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'grant' or 'revoke'"
            )
        
        updated_count = 0
        
        for user_id in bulk_update.user_ids:
            user = get_user(db, str(user_id))
            if not user:
                continue
                
            for permission_id in bulk_update.permission_ids:
                permission = get_permission(db, permission_id)
                if not permission:
                    continue
                    
                if bulk_update.action == 'grant':
                    if permission not in user.permissions:
                        user.permissions.append(permission)
                        updated_count += 1
                else:  # revoke
                    if permission in user.permissions:
                        user.permissions.remove(permission)
                        updated_count += 1
        
        db.commit()
        
        logger.info(f"Bulk permission update completed by admin {current_user.email}: {updated_count} changes")
        
        return {
            "message": f"Bulk permission update completed",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk permission update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk permission update failed"
        )

@router.post("/users/features/bulk")
async def bulk_update_user_features(
    bulk_update: BulkFeatureUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk grant or revoke features for multiple users"""
    try:
        if bulk_update.action not in ['grant', 'revoke']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'grant' or 'revoke'"
            )
        
        updated_count = 0
        
        for user_id in bulk_update.user_ids:
            user = get_user(db, str(user_id))
            if not user:
                continue
                
            for feature_id in bulk_update.feature_ids:
                feature = get_feature(db, feature_id)
                if not feature:
                    continue
                    
                if bulk_update.action == 'grant':
                    if feature not in user.features:
                        user.features.append(feature)
                        updated_count += 1
                else:  # revoke
                    if feature in user.features:
                        user.features.remove(feature)
                        updated_count += 1
        
        db.commit()
        
        logger.info(f"Bulk feature update completed by admin {current_user.email}: {updated_count} changes")
        
        return {
            "message": f"Bulk feature update completed",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk feature update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk feature update failed"
        ) 