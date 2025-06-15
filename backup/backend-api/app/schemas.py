"""
Pydantic schemas for Backend API Server
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration time")
    iat: int = Field(..., description="Issued at time")
    jti: str = Field(..., description="JWT ID")
    group: Optional[str] = Field(None, description="User group")
    department: Optional[str] = Field(None, description="User department")


class CurrentUser(BaseModel):
    """Current authenticated user schema"""
    id: int = Field(..., description="User ID")
    username: Optional[str] = Field(None, description="Username")
    group: Optional[str] = Field(None, description="User group")
    department: Optional[str] = Field(None, description="User department")


class ProtectedDataResponse(BaseModel):
    """Protected data response schema"""
    message: str = Field(..., description="Response message")
    user: CurrentUser = Field(..., description="Current user information")
    data: dict = Field(..., description="Protected data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(default="healthy", description="Service status")
    auth_server_status: str = Field(..., description="Auth server status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error detail")
    error_code: Optional[str] = Field(None, description="Error code")


class JWKSKey(BaseModel):
    """JWKS key schema"""
    kty: str = Field(..., description="Key type")
    use: str = Field(..., description="Key use")
    kid: str = Field(..., description="Key ID")
    alg: str = Field(..., description="Algorithm")
    n: str = Field(..., description="Modulus")
    e: str = Field(..., description="Exponent")


class JWKSResponse(BaseModel):
    """JWKS response schema"""
    keys: list[JWKSKey] = Field(..., description="List of keys") 