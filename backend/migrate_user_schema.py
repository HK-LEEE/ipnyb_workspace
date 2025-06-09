"""
사용자 테이블 스키마 마이그레이션
- 매핑 테이블 (user_role_mapping, user_group_mapping)의 데이터를 users 테이블로 통합
- role_id, group_id 컬럼을 users 테이블에 추가
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import CHAR

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_user_schema():
    """사용자 스키마 마이그레이션 실행"""
    
    # 데이터베이스 연결
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("🚀 사용자 스키마 마이그레이션 시작...")
        
        # 1. 기존 테이블 존재 여부 확인
        logger.info("📋 기존 테이블 확인 중...")
        
        # 테이블 존재 여부 확인
        tables_check = session.execute(text("""
            SELECT TABLE_NAME 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME IN ('users', 'user_role_mapping', 'user_group_mapping', 'roles', 'groups')
        """)).fetchall()
        
        existing_tables = [table[0] for table in tables_check]
        logger.info(f"✅ 존재하는 테이블: {existing_tables}")
        
        # 2. users 테이블에 role_id, group_id 컬럼 추가 (없는 경우)
        logger.info("🔧 users 테이블에 새 컬럼 추가 중...")
        
        # role_id 컬럼 추가
        try:
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role_id INT NULL COMMENT '사용자 역할 ID'
            """))
            logger.info("✅ role_id 컬럼 추가 완료")
        except Exception as e:
            if "Duplicate column name" in str(e):
                logger.info("ℹ️  role_id 컬럼이 이미 존재함")
            else:
                logger.warning(f"⚠️  role_id 컬럼 추가 실패: {e}")
        
        # group_id 컬럼 추가
        try:
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN group_id INT NULL COMMENT '사용자 그룹 ID'
            """))
            logger.info("✅ group_id 컬럼 추가 완료")
        except Exception as e:
            if "Duplicate column name" in str(e):
                logger.info("ℹ️  group_id 컬럼이 이미 존재함")
            else:
                logger.warning(f"⚠️  group_id 컬럼 추가 실패: {e}")
        
        # 3. 매핑 테이블에서 데이터 이전 (role_mapping)
        if 'user_role_mapping' in existing_tables:
            logger.info("📦 user_role_mapping 데이터 이전 중...")
            
            # 각 사용자의 첫 번째 역할을 users 테이블에 설정
            result = session.execute(text("""
                UPDATE users u
                JOIN (
                    SELECT user_id, MIN(role_id) as role_id
                    FROM user_role_mapping
                    GROUP BY user_id
                ) urm ON u.id = urm.user_id
                SET u.role_id = urm.role_id
                WHERE u.role_id IS NULL
            """))
            
            affected_roles = result.rowcount if hasattr(result, 'rowcount') else 0
            logger.info(f"✅ {affected_roles}개 사용자의 역할 데이터 이전 완료")
        
        # 4. 매핑 테이블에서 데이터 이전 (group_mapping)
        if 'user_group_mapping' in existing_tables:
            logger.info("📦 user_group_mapping 데이터 이전 중...")
            
            # 각 사용자의 첫 번째 그룹을 users 테이블에 설정
            result = session.execute(text("""
                UPDATE users u
                JOIN (
                    SELECT user_id, MIN(group_id) as group_id
                    FROM user_group_mapping
                    GROUP BY user_id
                ) ugm ON u.id = ugm.user_id
                SET u.group_id = ugm.group_id
                WHERE u.group_id IS NULL
            """))
            
            affected_groups = result.rowcount if hasattr(result, 'rowcount') else 0
            logger.info(f"✅ {affected_groups}개 사용자의 그룹 데이터 이전 완료")
        
        # 5. 외래 키 제약 조건 추가
        logger.info("🔗 외래 키 제약 조건 추가 중...")
        
        # role_id 외래 키
        try:
            session.execute(text("""
                ALTER TABLE users 
                ADD CONSTRAINT fk_users_role_id 
                FOREIGN KEY (role_id) REFERENCES roles(id)
                ON DELETE SET NULL ON UPDATE CASCADE
            """))
            logger.info("✅ role_id 외래 키 추가 완료")
        except Exception as e:
            if "Duplicate foreign key constraint name" in str(e) or "already exists" in str(e):
                logger.info("ℹ️  role_id 외래 키가 이미 존재함")
            else:
                logger.warning(f"⚠️  role_id 외래 키 추가 실패: {e}")
        
        # group_id 외래 키
        try:
            session.execute(text("""
                ALTER TABLE users 
                ADD CONSTRAINT fk_users_group_id 
                FOREIGN KEY (group_id) REFERENCES groups(id)
                ON DELETE SET NULL ON UPDATE CASCADE
            """))
            logger.info("✅ group_id 외래 키 추가 완료")
        except Exception as e:
            if "Duplicate foreign key constraint name" in str(e) or "already exists" in str(e):
                logger.info("ℹ️  group_id 외래 키가 이미 존재함")
            else:
                logger.warning(f"⚠️  group_id 외래 키 추가 실패: {e}")
        
        # 6. 변경사항 커밋
        session.commit()
        logger.info("💾 변경사항 커밋 완료")
        
        # 7. 매핑 테이블 백업 및 삭제 (선택사항)
        backup_choice = input("\n🗑️  매핑 테이블을 삭제하시겠습니까? (데이터 이전이 완료되었습니다) [y/N]: ")
        
        if backup_choice.lower() in ['y', 'yes']:
            # 매핑 테이블 삭제
            if 'user_role_mapping' in existing_tables:
                session.execute(text("DROP TABLE user_role_mapping"))
                logger.info("🗑️  user_role_mapping 테이블 삭제 완료")
            
            if 'user_group_mapping' in existing_tables:
                session.execute(text("DROP TABLE user_group_mapping"))
                logger.info("🗑️  user_group_mapping 테이블 삭제 완료")
            
            session.commit()
            logger.info("💾 매핑 테이블 삭제 커밋 완료")
        else:
            logger.info("ℹ️  매핑 테이블은 보존됩니다. 나중에 수동으로 삭제할 수 있습니다.")
        
        # 8. 마이그레이션 결과 확인
        logger.info("📊 마이그레이션 결과 확인 중...")
        
        result = session.execute(text("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(role_id) as users_with_role,
                COUNT(group_id) as users_with_group
            FROM users
        """)).fetchone()
        
        logger.info(f"""
✅ 마이그레이션 완료!
📈 결과 요약:
   - 총 사용자 수: {result.total_users}
   - 역할이 설정된 사용자: {result.users_with_role}
   - 그룹이 설정된 사용자: {result.users_with_group}
        """)
        
    except Exception as e:
        logger.error(f"❌ 마이그레이션 실패: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def rollback_migration():
    """마이그레이션 롤백 (매핑 테이블 복원)"""
    
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("🔄 마이그레이션 롤백 시작...")
        
        # 매핑 테이블 재생성
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_role_mapping (
                user_id CHAR(36) NOT NULL,
                role_id INT NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
            )
        """))
        
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_group_mapping (
                user_id CHAR(36) NOT NULL,
                group_id INT NOT NULL,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, group_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            )
        """))
        
        # users 테이블의 데이터를 매핑 테이블로 복사
        session.execute(text("""
            INSERT IGNORE INTO user_role_mapping (user_id, role_id)
            SELECT id, role_id FROM users WHERE role_id IS NOT NULL
        """))
        
        session.execute(text("""
            INSERT IGNORE INTO user_group_mapping (user_id, group_id)
            SELECT id, group_id FROM users WHERE group_id IS NOT NULL
        """))
        
        session.commit()
        logger.info("✅ 롤백 완료")
        
    except Exception as e:
        logger.error(f"❌ 롤백 실패: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="사용자 스키마 마이그레이션")
    parser.add_argument("--rollback", action="store_true", help="마이그레이션 롤백")
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
    else:
        migrate_user_schema() 