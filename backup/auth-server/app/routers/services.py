"""
Service management router
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryResponse,
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceWithCategory,
    UserResponse
)
from ..crud import (
    get_service_category, get_service_categories, get_service,
    get_services, create_service, get_user
)
from ..models import User, Service, ServiceCategory
from .auth import get_current_user, get_current_admin_user

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/services", tags=["Services"])

# ==================== SERVICE CATEGORIES ====================

@router.get("/categories", response_model=List[ServiceCategoryResponse])
async def get_service_categories_endpoint(
    current_user: User = Depends(get_current_user),
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

@router.get("/categories/{category_id}", response_model=ServiceCategoryResponse)
async def get_service_category_endpoint(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific service category"""
    try:
        category = get_service_category(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get service category error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service category"
        )

# ==================== SERVICES ====================

@router.get("/", response_model=List[ServiceWithCategory])
async def get_services_endpoint(
    category_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available services for current user"""
    try:
        # Get all services
        services = get_services(db, category_id)
        
        # Filter services based on user permissions and approvals
        available_services = []
        
        for service in services:
            # Check if service requires approval
            if service.requires_approval and not current_user.is_admin:
                # Check if user has been granted access to this service
                if current_user in service.authorized_users:
                    available_services.append(service)
            else:
                # Service doesn't require approval or user is admin
                available_services.append(service)
        
        return available_services
        
    except Exception as e:
        logger.error(f"Get services error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get services"
        )

@router.get("/{service_id}", response_model=ServiceWithCategory)
async def get_service_endpoint(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific service details"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Check if user has access to this service
        if service.requires_approval and not current_user.is_admin:
            if current_user not in service.authorized_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to this service requires approval"
                )
        
        return service
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service"
        )

@router.post("/{service_id}/request-access")
async def request_service_access(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request access to a service"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Check if service requires approval
        if not service.requires_approval:
            return {"message": "This service does not require approval"}
        
        # Check if user already has access
        if current_user in service.authorized_users:
            return {"message": "You already have access to this service"}
        
        logger.info(f"User {current_user.email} requested access to service {service.name}")
        
        return {
            "message": "Access request submitted. An administrator will review your request.",
            "service_name": service.display_name,
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request service access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request service access"
        )

@router.get("/{service_id}/launch")
async def launch_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Launch/access a service"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Check if user has access to this service
        if service.requires_approval and not current_user.is_admin:
            if current_user not in service.authorized_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access to this service requires approval"
                )
        
        # Log service access
        logger.info(f"User {current_user.email} accessed service {service.name}")
        
        # Return service launch information
        response = {
            "service_id": service.id,
            "name": service.name,
            "display_name": service.display_name,
            "url": service.url,
            "port": service.port,
            "is_external": service.is_external,
            "open_in_new_tab": service.open_in_new_tab,
            "message": f"Launching {service.display_name}..."
        }
        
        # If service has a specific port, include it in the URL
        if service.port and not service.is_external:
            response["launch_url"] = f"http://localhost:{service.port}"
        else:
            response["launch_url"] = service.url
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Launch service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to launch service"
        )

# ==================== ADMIN ENDPOINTS ====================

@router.post("/", response_model=ServiceResponse)
async def create_service_admin(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new service (admin only)"""
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

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service_admin(
    service_id: int,
    service_update: ServiceUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update service (admin only)"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Update service
        update_data = service_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)
        
        db.commit()
        db.refresh(service)
        
        logger.info(f"Service {service_id} updated by admin {current_user.email}")
        return service
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service update failed"
        )

@router.delete("/{service_id}")
async def delete_service_admin(
    service_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete service (admin only)"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Delete service
        db.delete(service)
        db.commit()
        
        logger.info(f"Service {service_id} deleted by admin {current_user.email}")
        return {"message": "Service deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service deletion failed"
        )

@router.post("/{service_id}/grant-access/{user_id}")
async def grant_service_access_admin(
    service_id: int,
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Grant user access to service (admin only)"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        user = get_user(db, str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user already has access
        if user in service.authorized_users:
            return {"message": "User already has access to this service"}
        
        # Grant access
        service.authorized_users.append(user)
        db.commit()
        
        logger.info(f"Admin {current_user.email} granted user {user.email} access to service {service.name}")
        
        return {
            "message": f"Access granted to {user.real_name} for {service.display_name}",
            "user": user.real_name,
            "service": service.display_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Grant service access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant service access"
        )

@router.delete("/{service_id}/revoke-access/{user_id}")
async def revoke_service_access_admin(
    service_id: int,
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke user access to service (admin only)"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        user = get_user(db, str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has access
        if user not in service.authorized_users:
            return {"message": "User does not have access to this service"}
        
        # Revoke access
        service.authorized_users.remove(user)
        db.commit()
        
        logger.info(f"Admin {current_user.email} revoked user {user.email} access from service {service.name}")
        
        return {
            "message": f"Access revoked from {user.real_name} for {service.display_name}",
            "user": user.real_name,
            "service": service.display_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Revoke service access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke service access"
        )

@router.get("/{service_id}/users", response_model=List[UserResponse])
async def get_service_users_admin(
    service_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get users who have access to service (admin only)"""
    try:
        service = get_service(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        return service.authorized_users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get service users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service users"
        ) 