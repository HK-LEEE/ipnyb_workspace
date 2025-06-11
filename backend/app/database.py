import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from .config import settings

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 베이스 클래스 생성
Base = declarative_base()

def get_database_url():
    """현재 설정된 데이터베이스 URL 반환"""
    return settings.database_url

def get_database_engine():
    """데이터베이스 타입에 따라 적절한 엔진 생성"""
    database_url = settings.database_url
    database_type = settings.database_type.lower()
    
    # 공통 엔진 설정
    common_args = {
        "echo": False,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "pool_timeout": 30,
        "max_overflow": 0
    }
    
    try:
        if database_type == "mysql":
            # MySQL 설정
            engine = create_engine(
                database_url,
                connect_args={"charset": "utf8mb4"},
                **common_args
            )
            logger.info(f"MySQL 데이터베이스 연결 시도: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
            
        elif database_type == "mssql":
            # MSSQL 설정
            engine = create_engine(
                database_url,
                connect_args={
                    "TrustServerCertificate": "yes",
                    "Encrypt": "no"
                },
                **common_args
            )
            logger.info(f"MSSQL 데이터베이스 연결 시도: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
            
        else:
            # 기본값은 MySQL
            engine = create_engine(
                settings.mysql_database_url,
                connect_args={"charset": "utf8mb4"},
                **common_args
            )
            logger.warning(f"알 수 없는 데이터베이스 타입: {database_type}. MySQL을 기본값으로 사용합니다.")
        
        # 연결 테스트
        with engine.connect() as connection:
            if database_type == "mysql":
                logger.info("✅ MySQL 데이터베이스 연결 성공")
            elif database_type == "mssql":
                logger.info("✅ MSSQL 데이터베이스 연결 성공")
            else:
                logger.info("✅ 데이터베이스 연결 성공")
                
        return engine
        
    except Exception as e:
        logger.error(f"❌ {database_type.upper()} 연결 실패: {e}")
        
        if database_type == "mysql":
            logger.info("MySQL 서버가 실행되고 있는지 확인하세요.")
            logger.info("설치 방법:")
            logger.info("1. XAMPP 설치 후 MySQL 시작")
            logger.info("2. MySQL Server 직접 설치")
            logger.info("3. Docker: docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0")
        elif database_type == "mssql":
            logger.info("SQL Server가 실행되고 있는지 확인하세요.")
            logger.info("설치 방법:")
            logger.info("1. SQL Server Express 설치")
            logger.info("2. Docker: docker run -d -p 1433:1433 -e SA_PASSWORD=YourPassword123 -e ACCEPT_EULA=Y mcr.microsoft.com/mssql/server:2019-latest")
            logger.info("3. ODBC Driver 17 for SQL Server 설치 필요")
        
        # 연결 실패시에도 mock 엔진 생성 (개발 환경에서 서버 시작 가능)
        engine = create_engine(
            "sqlite:///:memory:",  # 임시 SQLite 메모리 DB
            echo=False
        )
        logger.warning("⚠️  Mock 데이터베이스를 사용합니다. 일부 기능이 제한될 수 있습니다.")
        
        return engine

# 데이터베이스 엔진 생성
engine = get_database_engine()

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 데이터베이스 세션 의존성
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 세션 생성 실패: {str(e)}")
        # 더 상세한 에러 정보 출력
        import traceback
        logger.error(f"세부 에러: {traceback.format_exc()}")
        raise
    finally:
        try:
            if db:
                db.close()
        except Exception as e:
            logger.error(f"데이터베이스 세션 종료 실패: {str(e)}")
            pass

def create_tables():
    """모든 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"❌ 테이블 생성 실패: {e}")
        raise

def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            if settings.database_type.lower() == "mysql":
                result = connection.execute(text("SELECT 1")).fetchone()
            elif settings.database_type.lower() == "mssql":
                result = connection.execute(text("SELECT 1")).fetchone()
            else:
                result = connection.execute(text("SELECT 1")).fetchone()
            return True
    except Exception as e:
        logger.error(f"연결 테스트 실패: {e}")
        return False 