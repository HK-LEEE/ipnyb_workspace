"""
워크스페이스 테이블 마이그레이션 스크립트
jupyter_token 컬럼 추가
"""

from app.database import engine
from sqlalchemy import text

def migrate_workspace_table():
    """워크스페이스 테이블에 jupyter_token 컬럼 추가"""
    with engine.connect() as conn:
        try:
            # jupyter_token 컬럼이 있는지 확인
            result = conn.execute(text('SELECT jupyter_token FROM workspaces LIMIT 1'))
            print('jupyter_token 컬럼이 이미 존재합니다.')
        except Exception as e:
            print('jupyter_token 컬럼을 추가합니다...')
            try:
                conn.execute(text('ALTER TABLE workspaces ADD COLUMN jupyter_token VARCHAR(255)'))
                conn.commit()
                print('jupyter_token 컬럼이 성공적으로 추가되었습니다.')
            except Exception as e2:
                print(f'컬럼 추가 실패: {e2}')
        
        try:
            # path 컬럼이 있는지 확인 (workspace_path에서 변경)
            result = conn.execute(text('SELECT path FROM workspaces LIMIT 1'))
            print('path 컬럼이 이미 존재합니다.')
        except Exception as e:
            print('path 컬럼을 추가합니다...')
            try:
                # workspace_path가 있다면 path로 이름 변경
                try:
                    conn.execute(text('ALTER TABLE workspaces CHANGE workspace_path path VARCHAR(500)'))
                    conn.commit()
                    print('workspace_path 컬럼이 path로 변경되었습니다.')
                except:
                    # workspace_path가 없다면 새로 추가
                    conn.execute(text('ALTER TABLE workspaces ADD COLUMN path VARCHAR(500)'))
                    conn.commit()
                    print('path 컬럼이 성공적으로 추가되었습니다.')
            except Exception as e2:
                print(f'path 컬럼 처리 실패: {e2}')

if __name__ == "__main__":
    migrate_workspace_table() 