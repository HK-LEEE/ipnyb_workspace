import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from ..database import get_db
from ..services.workspace_service import WorkspaceService
from .auth import get_current_user

router = APIRouter(prefix="/files", tags=["Files"])

@router.get("/{workspace_id}/list")
async def list_files(
    workspace_id: int,
    path: str = "",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """워크스페이스 내 파일 목록 조회"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    target_path = os.path.join(workspace.path, path) if path else workspace.path
    
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    files = []
    for item in os.listdir(target_path):
        item_path = os.path.join(target_path, item)
        is_dir = os.path.isdir(item_path)
        size = os.path.getsize(item_path) if not is_dir else 0
        
        files.append({
            "name": item,
            "is_directory": is_dir,
            "size": size,
            "path": os.path.join(path, item) if path else item
        })
    
    return {"files": files, "current_path": path}

@router.post("/{workspace_id}/upload")
async def upload_file(
    workspace_id: int,
    path: str = "",
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """파일 업로드"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    upload_path = os.path.join(workspace.path, path) if path else workspace.path
    
    if not os.path.exists(upload_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload path not found"
        )
    
    uploaded_files = []
    
    for file in files:
        file_path = os.path.join(upload_path, file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "path": os.path.join(path, file.filename) if path else file.filename
            })
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename}: {str(e)}"
            )
    
    return {"message": "Files uploaded successfully", "files": uploaded_files}

@router.get("/{workspace_id}/download")
async def download_file(
    workspace_id: int,
    file_path: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """파일 다운로드"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    full_path = os.path.join(workspace.path, file_path)
    
    if not os.path.exists(full_path) or os.path.isdir(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    filename = os.path.basename(full_path)
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@router.delete("/{workspace_id}/delete")
async def delete_file(
    workspace_id: int,
    file_path: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """파일/폴더 삭제"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    full_path = os.path.join(workspace.path, file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File or directory not found"
        )
    
    try:
        if os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.post("/{workspace_id}/create-folder")
async def create_folder(
    workspace_id: int,
    folder_name: str,
    path: str = "",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """폴더 생성"""
    workspace_service = WorkspaceService(db)
    workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    parent_path = os.path.join(workspace.path, path) if path else workspace.path
    folder_path = os.path.join(parent_path, folder_name)
    
    if os.path.exists(folder_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder already exists"
        )
    
    try:
        os.makedirs(folder_path)
        return {"message": "Folder created successfully", "path": os.path.join(path, folder_name) if path else folder_name}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create folder: {str(e)}"
        ) 