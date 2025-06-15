"""
Configuration management for Backend API Server
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Auth Server Configuration
    auth_server_url: str = Field(
        default="http://localhost:8001",
        description="Auth server base URL"
    )
    jwks_url: str = Field(
        default="http://localhost:8001/auth/.well-known/jwks.json",
        description="JWKS endpoint URL"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=True, description="Debug mode")
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8001",
        description="Comma-separated list of allowed origins"
    )
    
    # JWT Configuration
    jwt_algorithm: str = Field(default="RS256", description="JWT algorithm")
    
    # Caching Configuration
    jwks_cache_ttl_minutes: int = Field(default=60, description="JWKS cache TTL in minutes")
    token_cache_ttl_minutes: int = Field(default=5, description="Token cache TTL in minutes")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="backend_api.log", description="Log file path")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings() 