"""
워크스페이스 폴더 구조 마이그레이션 스크립트
기존: data/users/{user_id}
변경: data/users/{user_id}/{workspace_id}
"""

import os
import shutil
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 현재 파일의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.models.workspace import Workspace
from app.models.user import User
from app.config import settings

def migrate_workspace_structure():
    """워크스페이스 폴더 구조 마이그레이션"""
    print("=== 워크스페이스 폴더 구조 마이그레이션 시작 ===")
    
    # 데이터베이스 연결
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 모든 활성 워크스페이스 조회
        workspaces = db.query(Workspace).filter(Workspace.is_active == True).all()
        
        print(f"총 {len(workspaces)}개의 워크스페이스를 마이그레이션합니다.")
        
        for workspace in workspaces:
            print(f"\n워크스페이스 마이그레이션: {workspace.name} (ID: {workspace.id})")
            
            # 기존 경로 (data/users/{user_id})
            old_user_path = settings.get_workspace_path(workspace.owner_id)
            
            # 새로운 경로 (data/users/{user_id}/{workspace_id})
            new_workspace_path = settings.get_workspace_path(workspace.owner_id, workspace.id)
            
            print(f"  기존 경로: {old_user_path}")
            print(f"  새 경로: {new_workspace_path}")
            
            # 기존 사용자 폴더가 존재하는 경우
            if os.path.exists(old_user_path):
                # 새로운 워크스페이스 폴더 생성
                Path(new_workspace_path).mkdir(parents=True, exist_ok=True)
                
                # 기존 폴더의 내용을 새 폴더로 복사
                if os.path.exists(old_user_path) and os.listdir(old_user_path):
                    print(f"  파일 복사 중...")
                    
                    for item in os.listdir(old_user_path):
                        old_item_path = os.path.join(old_user_path, item)
                        new_item_path = os.path.join(new_workspace_path, item)
                        
                        if os.path.isdir(old_item_path):
                            shutil.copytree(old_item_path, new_item_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(old_item_path, new_item_path)
                    
                    print(f"  파일 복사 완료")
                else:
                    print(f"  기존 폴더가 비어있거나 존재하지 않음")
            else:
                # 기존 폴더가 없는 경우 새로운 구조로 생성
                print(f"  새로운 워크스페이스 폴더 생성")
                Path(new_workspace_path).mkdir(parents=True, exist_ok=True)
                
                # 기본 폴더 생성
                Path(os.path.join(new_workspace_path, "notebooks")).mkdir(exist_ok=True)
                Path(os.path.join(new_workspace_path, "data")).mkdir(exist_ok=True)
                Path(os.path.join(new_workspace_path, "outputs")).mkdir(exist_ok=True)
            
            # 데이터베이스의 경로 업데이트
            workspace.path = new_workspace_path
            db.commit()
            
            print(f"  워크스페이스 경로 업데이트 완료")
        
        # 기존 사용자 폴더 정리 (선택사항)
        print("\n=== 기존 사용자 폴더 정리 ===")
        users = db.query(User).all()
        
        for user in users:
            old_user_path = settings.get_workspace_path(user.id)
            
            if os.path.exists(old_user_path):
                # 폴더가 비어있는지 확인
                if not os.listdir(old_user_path):
                    print(f"빈 폴더 삭제: {old_user_path}")
                    os.rmdir(old_user_path)
                else:
                    print(f"폴더에 파일이 남아있음 (수동 확인 필요): {old_user_path}")
        
        print("\n=== 마이그레이션 완료 ===")
        print("새로운 폴더 구조: data/users/{user_id}/{workspace_id}")
        
    except Exception as e:
        print(f"마이그레이션 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_workspace_structure() 