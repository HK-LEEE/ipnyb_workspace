"""
Workspace management router
"""

import logging
import os
import shutil
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceWithOwner,
    UserResponse, FileResponse, FileUpload
)
from ..crud import (
    get_workspace, get_user_workspaces, create_workspace, update_user,
    get_user
)
from ..models import User, Workspace
from .auth import get_current_user

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

# ==================== WORKSPACE MANAGEMENT ====================

@router.get("/", response_model=List[WorkspaceResponse])
async def get_user_workspaces_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's workspaces"""
    try:
        workspaces = get_user_workspaces(db, str(current_user.id))
        return workspaces
        
    except Exception as e:
        logger.error(f"Get workspaces error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workspaces"
        )

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace_endpoint(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new workspace"""
    try:
        # Check if user has workspace creation permission
        workspace_permissions = [p.name for p in current_user.permissions]
        if "workspace.create" not in workspace_permissions and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Workspace creation permission required"
            )
        
        workspace = create_workspace(db, workspace_data, str(current_user.id))
        
        # Create workspace directory
        workspace_dir = get_workspace_path(current_user.id, workspace.id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        logger.info(f"Workspace '{workspace.name}' created by user {current_user.email}")
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create workspace error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workspace creation failed"
        )

@router.get("/{workspace_id}", response_model=WorkspaceWithOwner)
async def get_workspace_endpoint(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workspace details"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user owns the workspace or is admin
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workspace"
        )

@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace_endpoint(
    workspace_id: int,
    workspace_update: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update workspace"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Update workspace
        update_data = workspace_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)
        
        workspace.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(workspace)
        
        logger.info(f"Workspace {workspace_id} updated by user {current_user.email}")
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update workspace error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workspace update failed"
        )

@router.delete("/{workspace_id}")
async def delete_workspace_endpoint(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete workspace"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Delete workspace directory
        workspace_dir = get_workspace_path(current_user.id, workspace.id)
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
        
        # Delete from database
        db.delete(workspace)
        db.commit()
        
        logger.info(f"Workspace {workspace_id} deleted by user {current_user.email}")
        return {"message": "Workspace deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete workspace error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workspace deletion failed"
        )

# ==================== FILE MANAGEMENT ====================

@router.get("/{workspace_id}/files")
async def list_workspace_files(
    workspace_id: int,
    path: str = Query("", description="Subdirectory path"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List files in workspace directory"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Get workspace directory
        workspace_dir = get_workspace_path(current_user.id, workspace.id)
        target_dir = os.path.join(workspace_dir, path) if path else workspace_dir
        
        if not os.path.exists(target_dir):
            return {"files": [], "directories": []}
        
        files = []
        directories = []
        
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "path": os.path.join(path, item) if path else item
                })
            elif os.path.isdir(item_path):
                directories.append({
                    "name": item,
                    "path": os.path.join(path, item) if path else item
                })
        
        return {
            "files": sorted(files, key=lambda x: x["name"]),
            "directories": sorted(directories, key=lambda x: x["name"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )

@router.post("/{workspace_id}/files/upload")
async def upload_file_to_workspace(
    workspace_id: int,
    path: str = Query("", description="Upload path within workspace"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file to workspace"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership and upload permission
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        file_permissions = [p.name for p in current_user.permissions]
        if "file.upload" not in file_permissions and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="File upload permission required"
            )
        
        # Create target directory
        workspace_dir = get_workspace_path(current_user.id, workspace.id)
        target_dir = os.path.join(workspace_dir, path) if path else workspace_dir
        os.makedirs(target_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(target_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file info
        stat = os.stat(file_path)
        
        logger.info(f"File '{file.filename}' uploaded to workspace {workspace_id} by user {current_user.email}")
        
        return {
            "filename": file.filename,
            "path": os.path.join(path, file.filename) if path else file.filename,
            "size": stat.st_size,
            "content_type": file.content_type,
            "uploaded_at": datetime.now(),
            "workspace_id": workspace_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

@router.delete("/{workspace_id}/files")
async def delete_file_from_workspace(
    workspace_id: int,
    file_path: str = Query(..., description="File path to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete file from workspace"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership and delete permission
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        file_permissions = [p.name for p in current_user.permissions]
        if "file.delete" not in file_permissions and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="File delete permission required"
            )
        
        # Get full file path
        workspace_dir = get_workspace_path(current_user.id, workspace.id)
        full_file_path = os.path.join(workspace_dir, file_path)
        
        # Security check: ensure path is within workspace
        if not full_file_path.startswith(workspace_dir):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
        
        if not os.path.exists(full_file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete file
        os.remove(full_file_path)
        
        logger.info(f"File '{file_path}' deleted from workspace {workspace_id} by user {current_user.email}")
        
        return {"message": f"File '{file_path}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File deletion failed"
        )

# ==================== JUPYTER INTEGRATION ====================

@router.post("/{workspace_id}/jupyter/start")
async def start_jupyter_server(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start Jupyter server for workspace"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership and Jupyter permission
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        jupyter_permissions = [p.name for p in current_user.permissions]
        if "jupyter.access" not in jupyter_permissions and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Jupyter access permission required"
            )
        
        # Find available port
        jupyter_port = find_available_port(8888, 9000)
        if not jupyter_port:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No available ports for Jupyter server"
            )
        
        # Update workspace with port
        workspace.jupyter_port = jupyter_port
        db.commit()
        
        # Start Jupyter server (implementation would depend on your setup)
        # This is a placeholder for the actual Jupyter server startup logic
        
        logger.info(f"Jupyter server started for workspace {workspace_id} on port {jupyter_port}")
        
        return {
            "message": "Jupyter server started",
            "port": jupyter_port,
            "url": f"http://localhost:{jupyter_port}",
            "workspace_id": workspace_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jupyter start error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start Jupyter server"
        )

@router.post("/{workspace_id}/jupyter/stop")
async def stop_jupyter_server(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop Jupyter server for workspace"""
    try:
        workspace = get_workspace(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check ownership
        if str(workspace.owner_id) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Stop Jupyter server (implementation would depend on your setup)
        # This is a placeholder for the actual Jupyter server shutdown logic
        
        # Clear port from workspace
        workspace.jupyter_port = None
        db.commit()
        
        logger.info(f"Jupyter server stopped for workspace {workspace_id}")
        
        return {"message": "Jupyter server stopped"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jupyter stop error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop Jupyter server"
        )

# ==================== UTILITY FUNCTIONS ====================

def get_workspace_path(user_id: UUID, workspace_id: int) -> str:
    """Get workspace directory path"""
    base_dir = os.getenv("DATA_DIR", "./data")
    return os.path.join(base_dir, "users", str(user_id), str(workspace_id))

def find_available_port(start_port: int, end_port: int) -> Optional[int]:
    """Find available port in range"""
    import socket
    
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    
    return None 