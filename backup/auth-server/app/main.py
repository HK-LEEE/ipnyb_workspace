"""
Central Authentication Server with Full Backend Integration
FastAPI application with comprehensive functionality
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from .database import engine, get_db, init_db
from .middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from .routers import auth, admin, workspace, services
from .security import SecurityManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize security manager
security_manager = SecurityManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("🚀 Starting Central Authentication Server...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize security manager
    try:
        await security_manager.initialize()
        logger.info("✅ Security manager initialized")
    except Exception as e:
        logger.error(f"❌ Security manager initialization failed: {e}")
        raise
    
    # Create data directories
    data_dir = os.getenv("DATA_DIR", "./data")
    directories = [
        data_dir,
        os.path.join(data_dir, "users"),
        os.path.join(data_dir, "uploads"),
        os.path.join(data_dir, "logs"),
        os.path.join(data_dir, "exports")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("✅ Data directories created")
    logger.info("🎉 Central Authentication Server started successfully!")
    
    yield
    
    logger.info("👋 Shutting down Central Authentication Server...")

# Create FastAPI application
app = FastAPI(
    title="Central Authentication Server",
    description="""
    ## Comprehensive Authentication & Data Platform
    
    A complete authentication server with integrated functionality including:
    
    ### 🔐 Authentication Features
    - OAuth 2.0 + JWT authentication with RS256
    - User registration with approval workflow
    - Role-based access control (RBAC)
    - Group and permission management
    - Refresh token rotation
    - Rate limiting and security headers
    
    ### 👥 User Management
    - Complete user profile management
    - Administrative user oversight
    - Bulk operations for permissions and features
    - Department and position tracking
    
    ### 🏢 Workspace Management
    - Personal workspace creation
    - File upload and management
    - Jupyter notebook integration
    - Collaborative workspace features
    
    ### 🛠️ Service Integration
    - Service category management
    - External service integration
    - Permission-based service access
    - Service monitoring and health checks
    
    ### 📊 Analytics & Monitoring
    - System statistics and metrics
    - User activity tracking
    - Performance monitoring
    - Audit logging
    
    ### 🤖 AI/LLM Integration
    - Multiple LLM provider support
    - AI-powered features
    - Jupyter AI integration
    - LLMOps workflow support
    
    Built with FastAPI, PostgreSQL, and modern security practices.
    """,
    version="2.0.0",
    contact={
        "name": "Central Auth System",
        "email": "admin@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /auth/login"
        },
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Administrative access"
                    }
                }
            }
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ==================== MIDDLEWARE ====================

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Trusted host middleware (production security)
if os.getenv("ENVIRONMENT", "development") == "production":
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001", 
        "http://127.0.0.1:8001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ==================== GLOBAL EXCEPTION HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed logging"""
    logger.warning(
        f"HTTP {exc.status_code} error at {request.method} {request.url}: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        f"Unexpected error at {request.method} {request.url}: {exc}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )

# ==================== ROUTERS ====================

# Authentication routes
app.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Authentication"]
)

# Administrative routes
app.include_router(
    admin.router,
    tags=["Administration"]
)

# Workspace management routes
app.include_router(
    workspace.router,
    tags=["Workspaces"]
)

# Service management routes
app.include_router(
    services.router,
    tags=["Services"]
)

# ==================== STATIC FILES ====================

# Create and mount static file directories
static_dirs = {
    "/static": os.path.join(os.getenv("DATA_DIR", "./data"), "static"),
    "/uploads": os.path.join(os.getenv("DATA_DIR", "./data"), "uploads"),
}

for mount_path, directory in static_dirs.items():
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    app.mount(mount_path, StaticFiles(directory=directory), name=mount_path.strip("/"))

# ==================== ROOT ENDPOINTS ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Central Authentication Server",
        "version": "2.0.0",
        "description": "Comprehensive authentication and data platform",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "OAuth 2.0 + JWT Authentication",
            "Role-based Access Control",
            "User Management",
            "Workspace Management", 
            "Service Integration",
            "AI/LLM Integration",
            "File Management",
            "Jupyter Integration",
            "Admin Dashboard",
            "Analytics & Monitoring"
        ],
        "endpoints": {
            "authentication": "/auth",
            "admin": "/admin",
            "workspaces": "/workspaces",
            "services": "/services",
            "documentation": "/docs",
            "health": "/health",
            "jwks": "/auth/.well-known/jwks.json"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check security manager
    try:
        security_status = "healthy" if security_manager.public_key else "unhealthy"
    except:
        security_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and security_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "components": {
            "database": db_status,
            "security": security_status,
            "api": "healthy"
        },
        "uptime": "N/A"  # Could implement uptime tracking
    }

@app.get("/info", tags=["Information"])
async def get_system_info():
    """Get system information"""
    return {
        "system": "Central Authentication Server",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database_type": "PostgreSQL",
        "authentication": "OAuth 2.0 + JWT (RS256)",
        "features": {
            "user_management": True,
            "role_based_access": True,
            "workspace_management": True,
            "file_management": True,
            "jupyter_integration": True,
            "llm_integration": True,
            "service_integration": True,
            "admin_dashboard": True,
            "rate_limiting": True,
            "security_headers": True,
            "audit_logging": True
        },
        "security": {
            "token_type": "JWT",
            "algorithm": "RS256",
            "access_token_expire": "15 minutes",
            "refresh_token_expire": "7 days",
            "refresh_token_rotation": True,
            "rate_limiting": True,
            "cors_enabled": True,
            "security_headers": True
        }
    }

# ==================== DEVELOPMENT ENDPOINTS ====================

if os.getenv("ENVIRONMENT", "development") == "development":
    
    @app.get("/dev/routes", tags=["Development"])
    async def list_routes():
        """List all available routes (development only)"""
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, 'name', 'N/A'),
                    "tags": getattr(route, 'tags', [])
                })
        
        return {
            "total_routes": len(routes),
            "routes": sorted(routes, key=lambda x: x["path"])
        }
    
    @app.get("/dev/config", tags=["Development"])
    async def get_config():
        """Get configuration information (development only)"""
        return {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database_url": os.getenv("DATABASE_URL", "Not set"),
            "cors_origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000", 
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://localhost:8001",
                "http://127.0.0.1:8001"
            ],
            "data_directory": os.getenv("DATA_DIR", "./data"),
            "log_level": "INFO"
        }

# ==================== APPLICATION STARTUP MESSAGE ====================

@app.on_event("startup")
async def startup_message():
    """Print startup message"""
    logger.info("""
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║                  Central Authentication Server                   ║
    ║                           Version 2.0.0                         ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  🔐 OAuth 2.0 + JWT Authentication                             ║
    ║  👥 Comprehensive User Management                               ║
    ║  🏢 Workspace & File Management                                 ║
    ║  🤖 AI/LLM Integration                                          ║
    ║  📊 Admin Dashboard & Analytics                                 ║
    ║  🛡️  Enterprise Security Features                               ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    🌍 Server running on: http://localhost:8001
    📚 API Documentation: http://localhost:8001/docs
    🔍 Alternative Docs: http://localhost:8001/redoc
    🔑 JWKS Endpoint: http://localhost:8001/auth/.well-known/jwks.json
    ⚡ Health Check: http://localhost:8001/health
    
    """)

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if os.getenv("ENVIRONMENT", "development") == "development" else False,
        log_level="info",
        access_log=True
    ) 