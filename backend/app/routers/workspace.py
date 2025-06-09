from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.workspace import WorkspaceCreate, WorkspaceResponse
from ..services.workspace_service import WorkspaceService
from .auth import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 워크스페이스 생성"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.create_workspace(workspace_data, current_user)
    return workspace

@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 워크스페이스 목록 조회"""
    workspace_service = WorkspaceService(db)
    workspaces = workspace_service.get_user_workspaces(current_user.id)
    return workspaces

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 워크스페이스 정보 조회"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return workspace

@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """워크스페이스 삭제"""
    workspace_service = WorkspaceService(db)
    success = workspace_service.delete_workspace(workspace_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    return {"message": "Workspace deleted successfully"} 