from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "mysql://test:test@localhost/jupyter_platform"
    
    # Jupyter
    jupyter_base_url: str = "http://localhost"
    jupyter_port_start: int = 8888
    jupyter_port_end: int = 9000
    
    # Workspace - 절대 경로로 설정
    workspace_base_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users")
    
    # App
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    def get_workspace_path(self, user_id: str) -> str:
        """사용자별 워크스페이스 경로 반환 (UUID 기반)"""
        base_path = os.path.abspath(self.workspace_base_path)
        return os.path.join(base_path, user_id)

settings = Settings() 