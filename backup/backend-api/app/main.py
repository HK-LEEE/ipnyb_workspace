"""
Main FastAPI application for Backend API Server (Resource Server)
"""

import logging
import sys
import requests
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .routers import protected
from .services.jwks_service import jwks_service
from .schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_auth_server_health() -> bool:
    """Check if auth server is reachable"""
    try:
        response = requests.get(f"{settings.auth_server_url}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Auth server health check failed: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Backend API Server...")
    
    # Check auth server connectivity
    if not check_auth_server_health():
        logger.warning("Auth server is not reachable, but continuing startup...")
    else:
        logger.info("Auth server connectivity verified")
    
    # Pre-load JWKS cache
    try:
        if jwks_service.get_jwks():
            logger.info("JWKS cache preloaded successfully")
        else:
            logger.warning("Failed to preload JWKS cache")
    except Exception as e:
        logger.warning(f"JWKS cache preload failed: {e}")
    
    logger.info("Backend API Server started successfully")
    
    yield
    
    logger.info("Shutting down Backend API Server...")


# Create FastAPI application
app = FastAPI(
    title="Backend API Server",
    description="Resource server with JWT token validation",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(protected.router)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Backend API Server",
        "version": "1.0.0",
        "status": "running",
        "auth_server": settings.auth_server_url,
        "endpoints": {
            "protected_data": "/api/protected-data",
            "user_profile": "/api/user-profile",
            "admin_only": "/api/admin-only",
            "it_department": "/api/it-department",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    try:
        # Check auth server status
        auth_server_status = "healthy" if check_auth_server_health() else "unhealthy"
        
        # Check JWKS availability
        jwks_available = jwks_service.get_jwks() is not None
        
        overall_status = "healthy" if auth_server_status == "healthy" and jwks_available else "degraded"
        
        return HealthResponse(
            status=overall_status,
            auth_server_status=auth_server_status,
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "auth_server_status": "error",
                "error": str(e),
                "version": "1.0.0"
            }
        )


@app.post("/admin/refresh-jwks")
async def refresh_jwks():
    """
    Admin endpoint to force refresh JWKS cache
    """
    try:
        success = jwks_service.refresh_cache()
        if success:
            return {"message": "JWKS cache refreshed successfully"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to refresh JWKS cache"
            )
    except Exception as e:
        logger.error(f"JWKS refresh error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during JWKS refresh"
        )


@app.get("/debug/jwks")
async def debug_jwks():
    """
    Debug endpoint to view current JWKS (only in debug mode)
    """
    if not settings.debug:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
    
    jwks = jwks_service.get_jwks()
    if jwks:
        return jwks
    else:
        raise HTTPException(
            status_code=503,
            detail="JWKS not available"
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        access_log=True,
        log_level=settings.log_level.lower()
    ) 