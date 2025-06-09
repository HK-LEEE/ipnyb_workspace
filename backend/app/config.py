from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="allow")
    
    # 데이터베이스 타입 및 연결 설정
    database_type: str = os.getenv("DATABASE_TYPE", "mysql")  # mysql 또는 mssql
    mysql_database_url: str = os.getenv("MYSQL_DATABASE_URL", "mysql+pymysql://test:test@localhost:3306/jupyter_platform")
    mssql_database_url: str = os.getenv("MSSQL_DATABASE_URL", "mssql+pyodbc://sa:password@localhost:1433/jupyter_platform?driver=ODBC+Driver+17+for+SQL+Server")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Jupyter
    jupyter_base_url: str = os.getenv("JUPYTER_BASE_URL", "http://localhost")
    jupyter_port_start: int = 8888
    jupyter_port_end: int = 9100  # 포트 범위 확장 (8888-9100, 총 212개 포트)
    
    # 워크스페이스 설정
    data_dir: str = os.path.abspath(os.getenv("DATA_DIR", "./data"))
    users_dir: str = os.path.join(data_dir, "users")
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM 설정들
    # Azure OpenAI 설정
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    
    # Ollama 설정
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_default_model: str = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2")
    
    # LLM 일반 설정
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")  # "azure" 또는 "ollama"
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    @property
    def database_url(self) -> str:
        """데이터베이스 타입에 따라 적절한 URL 반환"""
        if self.database_type.lower() == "mysql":
            return self.mysql_database_url
        elif self.database_type.lower() == "mssql":
            return self.mssql_database_url
        else:
            # 기본값은 MySQL
            return self.mysql_database_url
    
    def get_workspace_path(self, user_id: str, workspace_id: int = None) -> str:
        """워크스페이스 경로 생성 - data/users/{user_id}/{workspace_id} 형태"""
        if workspace_id is not None:
            return os.path.join(self.users_dir, user_id, str(workspace_id))
        else:
            # 호환성을 위해 workspace_id가 없으면 기본 사용자 폴더 반환
            return os.path.join(self.users_dir, user_id)

settings = Settings() 