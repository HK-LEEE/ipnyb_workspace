"""
Configuration management for Auth Server
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/auth_system",
        description="Database connection URL"
    )
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-here-change-this-in-production",
        description="Secret key for JWT signing"
    )
    jwt_algorithm: str = Field(default="RS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(default=15, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")
    
    # RSA Keys
    jwt_private_key_path: str = Field(default="./keys/private_key.pem", description="Private key file path")
    jwt_public_key_path: str = Field(default="./keys/public_key.pem", description="Public key file path")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8001, description="Server port")
    debug: bool = Field(default=True, description="Debug mode")
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed origins"
    )
    
    # Rate Limiting Configuration
    rate_limit_requests_per_minute: int = Field(default=10, description="Rate limit requests per minute")
    rate_limit_block_duration_minutes: int = Field(default=15, description="Rate limit block duration in minutes")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="auth_server.log", description="Log file path")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings() 