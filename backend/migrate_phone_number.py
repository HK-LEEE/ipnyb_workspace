import os
import sys
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database_url, engine

def migrate_add_phone_number():
    """users 테이블에 phone_number 컬럼 추가"""
    
    print("🔄 데이터베이스 마이그레이션 시작: phone_number 컬럼 추가")
    
    try:
        # 연결 테스트
        with engine.connect() as connection:
            # phone_number 컬럼이 이미 존재하는지 확인

            
            # 기존 사용자들에게 샘플 전화번호 추가
            print("📝 기존 사용자들에게 샘플 전화번호 추가 중...")
            
            # admin 사용자 전화번호 업데이트
            connection.execute(text("""
                UPDATE users 
                SET phone_number = '010-1234-5678' 
                WHERE email = 'admin@jupyter-platform.com'
            """))
            
            # test 사용자 전화번호 업데이트
            connection.execute(text("""
                UPDATE users 
                SET phone_number = '010-9876-5432' 
                WHERE email = 'test@example.com'
            """))
            
            connection.commit()
            print("✅ 기존 사용자 전화번호 업데이트 완료")
            
            return True
            
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False

def add_sample_data():
    """추가 샘플 데이터 생성"""
    
    print("📊 샘플 데이터 추가 중...")
    
    try:
        with engine.connect() as connection:
            
            # 추가 샘플 사용자들 생성
            sample_users = [
                {
                    'username': 'manager1',
                    'email': 'manager1@jupyter-platform.com',
                    'phone_number': '010-1111-2222',
                    'password': '$2b$12$KvN2kuwHwd0dnmXPkQ/NAOA60vXyRkApp0E5cH6icZtRm46hjdXRm',  # manager123!
                    'is_admin': False
                },
                {
                    'username': 'user1',
                    'email': 'user1@jupyter-platform.com', 
                    'phone_number': '010-3333-4444',
                    'password': '$2b$12$tPFBxm1WGZYmsmgAXpAt0uE3TCLC1uws.Fd89KKTXJm9.F7rbiyy.',  # user123!
                    'is_admin': False
                },
                {
                    'username': 'developer1',
                    'email': 'dev1@jupyter-platform.com',
                    'phone_number': '010-5555-6666', 
                    'password': '$2b$12$tRg3AdgXLHsbRcFoInZ0YOa31i3Tm68Ub.xE3ExnB9Q1vaT9YZJFW',  # dev123!
                    'is_admin': False
                }
            ]
            
            for user in sample_users:
                # 이미 존재하는지 확인
                result = connection.execute(text("""
                    SELECT id FROM users WHERE email = :email
                """), {'email': user['email']})
                
                if not result.fetchone():
                    connection.execute(text("""
                        INSERT INTO users (username, email, phone_number, hashed_password, is_active, is_admin, created_at, updated_at)
                        VALUES (:username, :email, :phone_number, :password, TRUE, :is_admin, NOW(), NOW())
                    """), {
                        'username': user['username'],
                        'email': user['email'], 
                        'phone_number': user['phone_number'],
                        'password': user['password'],
                        'is_admin': user['is_admin']
                    })
                    print(f"  ✅ 사용자 생성: {user['username']} ({user['email']})")
                else:
                    print(f"  ⏭️  이미 존재: {user['username']} ({user['email']})")
            
            # 사용자-역할 매핑 추가
            print("🔗 사용자-역할 매핑 추가 중...")
            
            # manager1을 manager 역할에 할당
            connection.execute(text("""
                INSERT IGNORE INTO user_role_mapping (user_id, role_id, assigned_at)
                SELECT u.id, r.id, NOW()
                FROM users u, `roles` r 
                WHERE u.email = 'manager1@jupyter-platform.com' AND r.name = 'manager'
            """))
            
            # user1을 user 역할에 할당  
            connection.execute(text("""
                INSERT IGNORE INTO user_role_mapping (user_id, role_id, assigned_at)
                SELECT u.id, r.id, NOW()
                FROM users u, `roles` r 
                WHERE u.email = 'user1@jupyter-platform.com' AND r.name = 'user'
            """))
            
            # developer1을 user 역할에 할당
            connection.execute(text("""
                INSERT IGNORE INTO user_role_mapping (user_id, role_id, assigned_at)
                SELECT u.id, r.id, NOW()
                FROM users u, `roles` r 
                WHERE u.email = 'dev1@jupyter-platform.com' AND r.name = 'user'
            """))
            
            # 사용자-그룹 매핑 추가
            print("👥 사용자-그룹 매핑 추가 중...")
            
            # 모든 새 사용자를 Default Users 그룹에 추가
            for email in ['manager1@jupyter-platform.com', 'user1@jupyter-platform.com', 'dev1@jupyter-platform.com']:
                connection.execute(text("""
                    INSERT IGNORE INTO user_group_mapping (user_id, group_id, joined_at)
                    SELECT u.id, g.id, NOW()
                    FROM users u, `groups` g 
                    WHERE u.email = :email AND g.name = 'Default Users'
                """), {'email': email})
            
            # developer1을 Developers 그룹에도 추가
            connection.execute(text("""
                INSERT IGNORE INTO user_group_mapping (user_id, group_id, joined_at)
                SELECT u.id, g.id, NOW()
                FROM users u, `groups` g 
                WHERE u.email = 'dev1@jupyter-platform.com' AND g.name = 'Developers'
            """))
            
            connection.commit()
            print("✅ 샘플 데이터 추가 완료")
            
            return True
            
    except Exception as e:
        print(f"❌ 샘플 데이터 추가 실패: {e}")
        return False

def verify_data():
    """데이터 확인"""
    
    print("🔍 데이터베이스 상태 확인...")
    
    try:
        with engine.connect() as connection:
            # 사용자 목록 확인
            result = connection.execute(text("""
                SELECT u.username, u.email, u.phone_number, u.is_admin,
                       GROUP_CONCAT(DISTINCT r.name) as roles,
                       GROUP_CONCAT(DISTINCT g.name) as group_names
                FROM users u
                LEFT JOIN user_role_mapping urm ON u.id = urm.user_id
                LEFT JOIN `roles` r ON urm.role_id = r.id
                LEFT JOIN user_group_mapping ugm ON u.id = ugm.user_id  
                LEFT JOIN `groups` g ON ugm.group_id = g.id
                GROUP BY u.id
                ORDER BY u.created_at
            """))
            
            print("\n📋 등록된 사용자 목록:")
            print("-" * 80)
            for row in result:
                print(f"👤 {row.username} ({row.email})")
                print(f"   📱 전화번호: {row.phone_number or 'None'}")
                print(f"   👑 관리자: {'Yes' if row.is_admin else 'No'}")
                print(f"   🎭 역할: {row.roles or 'None'}")
                print(f"   👥 그룹: {row.group_names or 'None'}")
                print("-" * 80)
            
            # 테이블 개수 확인
            tables = ['users', '`roles`', '`groups`', 'user_role_mapping', 'user_group_mapping']
            print("\n📊 테이블별 레코드 수:")
            for table in tables:
                result = connection.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                count = result.fetchone().count
                print(f"  📄 {table}: {count}개")
            
    except Exception as e:
        print(f"❌ 데이터 확인 실패: {e}")

if __name__ == "__main__":
    print("🚀 데이터베이스 마이그레이션 및 샘플 데이터 추가 시작")
    print("=" * 60)
    
    # 1. phone_number 컬럼 추가
    if migrate_add_phone_number():
        # 2. 샘플 데이터 추가
        if add_sample_data():
            # 3. 데이터 확인
            verify_data()
            print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
            print("\n📝 사용 가능한 계정:")
            print("  👑 admin@jupyter-platform.com / admin123! (관리자)")
            print("  👤 test@example.com / test123! (일반 사용자)")
            print("  👨‍💼 manager1@jupyter-platform.com / manager123! (매니저)")
            print("  👤 user1@jupyter-platform.com / user123! (일반 사용자)")
            print("  👨‍💻 dev1@jupyter-platform.com / dev123! (개발자)")
        else:
            print("❌ 샘플 데이터 추가 실패")
    else:
        print("❌ 마이그레이션 실패") 