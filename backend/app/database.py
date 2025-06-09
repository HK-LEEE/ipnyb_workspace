import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 베이스 클래스 생성
Base = declarative_base()

def get_database_url():
    """환경변수에 따라 데이터베이스 URL 반환"""
    # DATABASE_URL이 직접 설정되어 있는 경우
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # 개별 설정값으로 URL 구성
    user = os.getenv("DB_USER", "test")
    password = os.getenv("DB_PASSWORD", "test")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "jupyter_platform")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

# 데이터베이스 엔진 생성 (호환성 향상을 위한 설정 추가)
database_url = get_database_url()

try:
    engine = create_engine(
        database_url,
        echo=False,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={"charset": "utf8mb4"},
        pool_timeout=30,
        max_overflow=0
    )
    
    # 연결 테스트
    with engine.connect() as connection:
        logger.info("MySQL 데이터베이스 연결 성공")
        
except Exception as e:
    logger.error(f"MySQL 연결 실패: {e}")
    logger.info("MySQL 서버가 실행되고 있는지 확인하세요.")
    logger.info("다음 방법 중 하나를 사용하여 MySQL을 설치/실행하세요:")
    logger.info("1. XAMPP 설치 후 MySQL 시작")
    logger.info("2. MySQL Server 직접 설치")
    logger.info("3. Docker로 MySQL 컨테이너 실행")
    
    # 연결 실패시에도 engine 객체 생성 (일부 기능은 제한됨)
    engine = create_engine(
        database_url,
        echo=False,
        strategy='mock',
        executor=lambda sql, *_: None
    )

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
        raise
    finally:
        try:
            if db:
                db.close()
        except:
            pass

def create_tables():
    """모든 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"테이블 생성 실패: {e}")
        raise

def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1").fetchone()
            return True
    except Exception as e:
        logger.error(f"연결 테스트 실패: {e}")
        return False 