from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..services.workspace_service import WorkspaceService
from ..services.jupyter_service import jupyter_service
from .auth import get_current_user

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jupyter", tags=["Jupyter"])

@router.post("/start/{workspace_id}")
async def start_jupyter(
    workspace_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Jupyter Lab 인스턴스 시작"""
    try:
        logger.info(f"Jupyter Lab 시작 요청 - workspace_id: {workspace_id}, user_id: {current_user.id}")
        
        workspace_service = WorkspaceService(db)
        workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
        
        if not workspace:
            logger.error(f"워크스페이스를 찾을 수 없음 - workspace_id: {workspace_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        logger.info(f"워크스페이스 찾음 - name: {workspace.name}, path: {workspace.path}")
        
        # Jupyter Lab 시작
        logger.info("Jupyter Lab 시작 중...")
        port, token = jupyter_service.start_jupyter_lab(workspace)
        logger.info(f"Jupyter Lab 시작 완료 - port: {port}, token: {token[:20]}...")
        
        # 데이터베이스에 Jupyter 정보 업데이트
        logger.info("데이터베이스 업데이트 중...")
        updated_workspace = workspace_service.update_jupyter_info(workspace_id, port, token)
        
        if not updated_workspace:
            logger.error("워크스페이스 업데이트 실패")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update workspace with Jupyter info"
            )
        
        logger.info("데이터베이스 업데이트 완료")
        
        # 업데이트된 워크스페이스로 URL 생성
        jupyter_url = jupyter_service.get_jupyter_url(updated_workspace)
        logger.info(f"Jupyter URL 생성 완료: {jupyter_url}")
        
        return {
            "message": "Jupyter Lab started successfully",
            "port": port,
            "token": token,
            "url": jupyter_url,
            "auto_login_url": f"http://localhost:{port}/lab?token={token}",
            "direct_url": f"http://localhost:{port}/?token={token}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jupyter Lab 시작 실패: {str(e)}", exc_info=True)
        # Jupyter 프로세스가 시작되었지만 다른 에러가 발생한 경우 정리
        try:
            jupyter_service.stop_jupyter_lab(workspace_id)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Jupyter Lab 시작 실패: {str(e)}"
        )

@router.post("/stop/{workspace_id}")
async def stop_jupyter(
    workspace_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Jupyter Lab 인스턴스 중지"""
    try:
        workspace_service = WorkspaceService(db)
        workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        success = jupyter_service.stop_jupyter_lab(workspace_id)
        
        if success:
            # 데이터베이스에서 Jupyter 정보 제거
            workspace_service.update_jupyter_info(workspace_id, None, None)
            return {"message": "Jupyter Lab stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop Jupyter Lab"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Jupyter Lab 중지 실패: {str(e)}"
        )

@router.get("/status/{workspace_id}")
async def get_jupyter_status(
    workspace_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Jupyter Lab 인스턴스 상태 조회"""
    try:
        workspace_service = WorkspaceService(db)
        workspace = workspace_service.get_workspace_by_id(workspace_id, current_user.id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        is_running = jupyter_service.is_process_running(workspace_id)
        jupyter_url = jupyter_service.get_jupyter_url(workspace) if is_running else None
        
        return {
            "workspace_id": workspace_id,
            "is_running": is_running,
            "port": workspace.jupyter_port if is_running else None,
            "url": jupyter_url
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"상태 조회 실패: {str(e)}"
        ) 