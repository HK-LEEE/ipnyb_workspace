"""
Protected routes that require authentication
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ..schemas import ProtectedDataResponse, CurrentUser
from ..dependencies.auth import get_current_user, require_group, require_department

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["protected"])


@router.get("/protected-data", response_model=ProtectedDataResponse)
async def get_protected_data(current_user: CurrentUser = Depends(get_current_user)):
    """
    Example protected endpoint that requires authentication
    
    This endpoint demonstrates how to use the get_current_user dependency
    to protect routes and access user information from JWT tokens.
    """
    logger.info(f"Protected data requested by user: {current_user.id}")
    
    # Example protected data - in a real application, this would come from a database
    protected_data = {
        "sensitive_info": "This is protected information",
        "user_specific_data": f"Data for user {current_user.id}",
        "server_info": "Backend API Server v1.0.0",
        "access_time": datetime.utcnow().isoformat()
    }
    
    # Add group/department specific data
    if current_user.group == "admin":
        protected_data["admin_data"] = "This is admin-only information"
    
    if current_user.department:
        protected_data["department_data"] = f"Department-specific data for {current_user.department}"
    
    return ProtectedDataResponse(
        message="Successfully retrieved protected data",
        user=current_user,
        data=protected_data,
        timestamp=datetime.utcnow()
    )


@router.get("/admin-only")
async def admin_only_endpoint(current_user: CurrentUser = Depends(require_group("admin"))):
    """
    Endpoint that requires admin group access
    """
    logger.info(f"Admin endpoint accessed by user: {current_user.id}")
    
    return {
        "message": "This is admin-only content",
        "user": current_user,
        "admin_data": {
            "total_users": 100,  # Example admin data
            "system_status": "healthy",
            "last_backup": "2024-01-01T00:00:00Z"
        }
    }


@router.get("/it-department")
async def it_department_endpoint(current_user: CurrentUser = Depends(require_department("IT"))):
    """
    Endpoint that requires IT department access
    """
    logger.info(f"IT department endpoint accessed by user: {current_user.id}")
    
    return {
        "message": "This is IT department content",
        "user": current_user,
        "it_data": {
            "server_metrics": {"cpu": "45%", "memory": "67%", "disk": "32%"},
            "pending_tickets": 12,
            "system_alerts": 3
        }
    }


@router.get("/user-profile")
async def get_user_profile(current_user: CurrentUser = Depends(get_current_user)):
    """
    Get current user's profile information
    """
    logger.info(f"Profile requested by user: {current_user.id}")
    
    return {
        "message": "User profile retrieved successfully",
        "profile": {
            "id": current_user.id,
            "group": current_user.group,
            "department": current_user.department,
            "access_level": "authenticated",
            "last_login": datetime.utcnow().isoformat()
        }
    }


@router.post("/secure-action")
async def perform_secure_action(
    action_data: dict,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Example of a secure action that requires authentication
    """
    logger.info(f"Secure action performed by user: {current_user.id}")
    
    # Validate action based on user permissions
    if current_user.group not in ["admin", "user"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for this action"
        )
    
    # Process the action (this is just an example)
    result = {
        "action": "completed",
        "performed_by": current_user.id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": action_data
    }
    
    return {
        "message": "Secure action completed successfully",
        "result": result
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint (no authentication required)
    """
    return {
        "status": "healthy",
        "service": "Backend API Server",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    } 