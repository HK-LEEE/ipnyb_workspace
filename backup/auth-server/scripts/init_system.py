#!/usr/bin/env python3
"""
Central Authentication System Initialization Script

This script initializes the system with:
- Database tables
- Default roles, permissions, and features
- Service categories and basic services
- Default admin user
- Sample data for testing
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, init_db
from app.models import (
    User, Role, Group, Permission, Feature, ServiceCategory, Service
)
from app.crud import (
    get_role_by_name, get_group_by_name, get_permission_by_name, 
    get_feature_by_name, create_role, create_group, create_permission, 
    create_feature, get_password_hash
)
from app.schemas import (
    RoleCreate, GroupCreate, PermissionCreate, FeatureCreate,
    ServiceCategoryCreate, ServiceCreate
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_default_permissions(db):
    """Create default permissions"""
    permissions = [
        # Basic permissions
        {"name": "user.read", "display_name": "Read User Data", "description": "Read user profile information", "category": "basic"},
        {"name": "user.update", "display_name": "Update User Data", "description": "Update user profile information", "category": "basic"},
        
        # Workspace permissions
        {"name": "workspace.create", "display_name": "Create Workspace", "description": "Create new workspaces", "category": "workspace"},
        {"name": "workspace.read", "display_name": "Read Workspace", "description": "Access workspace data", "category": "workspace"},
        {"name": "workspace.update", "display_name": "Update Workspace", "description": "Modify workspace settings", "category": "workspace"},
        {"name": "workspace.delete", "display_name": "Delete Workspace", "description": "Delete workspaces", "category": "workspace"},
        
        # File permissions
        {"name": "file.upload", "display_name": "Upload Files", "description": "Upload files to workspaces", "category": "file"},
        {"name": "file.download", "display_name": "Download Files", "description": "Download files from workspaces", "category": "file"},
        {"name": "file.delete", "display_name": "Delete Files", "description": "Delete files from workspaces", "category": "file"},
        
        # Jupyter permissions
        {"name": "jupyter.access", "display_name": "Access Jupyter", "description": "Access Jupyter notebook environments", "category": "jupyter"},
        {"name": "jupyter.admin", "display_name": "Jupyter Admin", "description": "Administrative access to Jupyter environments", "category": "jupyter"},
        
        # LLM permissions
        {"name": "llm.access", "display_name": "Access LLM", "description": "Access large language model features", "category": "llm"},
        {"name": "llm.admin", "display_name": "LLM Admin", "description": "Administrative access to LLM features", "category": "llm"},
        
        # Admin permissions
        {"name": "admin.users", "display_name": "User Administration", "description": "Manage users and permissions", "category": "admin"},
        {"name": "admin.system", "display_name": "System Administration", "description": "Full system administration", "category": "admin"},
        {"name": "admin.services", "display_name": "Service Administration", "description": "Manage services and integrations", "category": "admin"},
    ]
    
    created_count = 0
    for perm_data in permissions:
        if not get_permission_by_name(db, perm_data["name"]):
            permission = Permission(**perm_data)
            db.add(permission)
            created_count += 1
    
    db.commit()
    logger.info(f"Created {created_count} default permissions")

async def create_default_features(db):
    """Create default features"""
    features = [
        # Core features
        {"name": "profile_management", "display_name": "Profile Management", "description": "Manage user profile and settings", "category": "core", "icon": "user", "auto_grant": True, "requires_approval": False},
        {"name": "workspace_basic", "display_name": "Basic Workspace", "description": "Create and manage personal workspaces", "category": "core", "icon": "folder", "auto_grant": True, "requires_approval": False},
        
        # Analysis features
        {"name": "jupyter_notebooks", "display_name": "Jupyter Notebooks", "description": "Access to Jupyter notebook environments", "category": "analysis", "icon": "code", "auto_grant": False, "requires_approval": True},
        {"name": "data_analysis", "display_name": "Data Analysis Tools", "description": "Advanced data analysis capabilities", "category": "analysis", "icon": "chart-bar", "auto_grant": False, "requires_approval": True},
        
        # AI features
        {"name": "llm_chat", "display_name": "LLM Chat", "description": "Chat with large language models", "category": "ai", "icon": "chat", "auto_grant": False, "requires_approval": True},
        {"name": "ai_assistant", "display_name": "AI Assistant", "description": "AI-powered coding and analysis assistant", "category": "ai", "icon": "robot", "auto_grant": False, "requires_approval": True},
        
        # Utility features
        {"name": "file_manager", "display_name": "File Manager", "description": "Advanced file management capabilities", "category": "utility", "icon": "folder-open", "auto_grant": True, "requires_approval": False},
        {"name": "export_tools", "display_name": "Export Tools", "description": "Export data and analysis results", "category": "utility", "icon": "download", "auto_grant": False, "requires_approval": True},
        
        # Admin features
        {"name": "user_management", "display_name": "User Management", "description": "Manage users and permissions", "category": "admin", "icon": "users", "auto_grant": False, "requires_approval": True},
        {"name": "system_admin", "display_name": "System Administration", "description": "Full system administration access", "category": "admin", "icon": "cog", "auto_grant": False, "requires_approval": True},
    ]
    
    created_count = 0
    for feature_data in features:
        if not get_feature_by_name(db, feature_data["name"]):
            feature = Feature(**feature_data)
            db.add(feature)
            created_count += 1
    
    db.commit()
    logger.info(f"Created {created_count} default features")

async def create_default_roles(db):
    """Create default roles"""
    roles_data = [
        {
            "name": "admin",
            "description": "System administrator with full access",
            "permissions": ["admin.users", "admin.system", "admin.services", "user.read", "user.update", 
                          "workspace.create", "workspace.read", "workspace.update", "workspace.delete",
                          "file.upload", "file.download", "file.delete", "jupyter.access", "jupyter.admin",
                          "llm.access", "llm.admin"],
            "features": ["profile_management", "workspace_basic", "jupyter_notebooks", "data_analysis",
                        "llm_chat", "ai_assistant", "file_manager", "export_tools", "user_management", "system_admin"]
        },
        {
            "name": "user",
            "description": "Standard user with basic access",
            "permissions": ["user.read", "user.update", "workspace.create", "workspace.read", 
                          "workspace.update", "file.upload", "file.download"],
            "features": ["profile_management", "workspace_basic", "file_manager"]
        },
        {
            "name": "analyst",
            "description": "Data analyst with advanced analysis tools",
            "permissions": ["user.read", "user.update", "workspace.create", "workspace.read", 
                          "workspace.update", "workspace.delete", "file.upload", "file.download", 
                          "file.delete", "jupyter.access", "llm.access"],
            "features": ["profile_management", "workspace_basic", "jupyter_notebooks", "data_analysis",
                        "llm_chat", "file_manager", "export_tools"]
        },
        {
            "name": "developer",
            "description": "Developer with coding and AI tools",
            "permissions": ["user.read", "user.update", "workspace.create", "workspace.read", 
                          "workspace.update", "workspace.delete", "file.upload", "file.download", 
                          "file.delete", "jupyter.access", "llm.access"],
            "features": ["profile_management", "workspace_basic", "jupyter_notebooks", "data_analysis",
                        "llm_chat", "ai_assistant", "file_manager", "export_tools"]
        }
    ]
    
    created_count = 0
    for role_data in roles_data:
        if not get_role_by_name(db, role_data["name"]):
            # Create role
            role = Role(
                name=role_data["name"],
                description=role_data["description"]
            )
            db.add(role)
            db.flush()  # Get the ID
            
            # Add permissions
            for perm_name in role_data["permissions"]:
                permission = get_permission_by_name(db, perm_name)
                if permission:
                    role.permissions.append(permission)
            
            # Add features
            for feature_name in role_data["features"]:
                feature = get_feature_by_name(db, feature_name)
                if feature:
                    role.features.append(feature)
            
            created_count += 1
    
    db.commit()
    logger.info(f"Created {created_count} default roles")

async def create_default_groups(db):
    """Create default groups"""
    groups = [
        {"name": "Default Users", "description": "Default group for all users"},
        {"name": "IT Department", "description": "Information Technology department"},
        {"name": "Data Science Team", "description": "Data science and analytics team"},
        {"name": "Development Team", "description": "Software development team"},
        {"name": "Research Team", "description": "Research and development team"},
    ]
    
    created_count = 0
    for group_data in groups:
        if not get_group_by_name(db, group_data["name"]):
            group = Group(
                name=group_data["name"],
                description=group_data["description"]
            )
            db.add(group)
            created_count += 1
    
    db.commit()
    logger.info(f"Created {created_count} default groups")

async def create_service_categories(db):
    """Create default service categories"""
    categories = [
        {"name": "development", "display_name": "Development Tools", "description": "Development and coding tools", "icon": "code", "color": "#007bff", "sort_order": 1},
        {"name": "data_science", "display_name": "Data Science", "description": "Data analysis and machine learning tools", "icon": "chart-line", "color": "#28a745", "sort_order": 2},
        {"name": "productivity", "display_name": "Productivity", "description": "Productivity and collaboration tools", "icon": "briefcase", "color": "#ffc107", "sort_order": 3},
        {"name": "ai_ml", "display_name": "AI & Machine Learning", "description": "Artificial intelligence and machine learning services", "icon": "brain", "color": "#6f42c1", "sort_order": 4},
        {"name": "database", "display_name": "Databases", "description": "Database management systems", "icon": "database", "color": "#dc3545", "sort_order": 5},
        {"name": "monitoring", "display_name": "Monitoring", "description": "System monitoring and observability", "icon": "chart-bar", "color": "#17a2b8", "sort_order": 6},
    ]
    
    created_count = 0
    for cat_data in categories:
        existing = db.query(ServiceCategory).filter(ServiceCategory.name == cat_data["name"]).first()
        if not existing:
            category = ServiceCategory(**cat_data)
            db.add(category)
            created_count += 1
    
    db.commit()
    logger.info(f"Created {created_count} service categories")

async def create_default_services(db):
    """Create default services"""
    # Get category IDs
    dev_cat = db.query(ServiceCategory).filter(ServiceCategory.name == "development").first()
    ds_cat = db.query(ServiceCategory).filter(ServiceCategory.name == "data_science").first()
    ai_cat = db.query(ServiceCategory).filter(ServiceCategory.name == "ai_ml").first()
    
    services = [
        {
            "name": "jupyter_lab",
            "display_name": "JupyterLab",
            "description": "Interactive development environment for Jupyter notebooks",
            "category_id": ds_cat.id if ds_cat else None,
            "icon": "jupyter",
            "url": "http://localhost:8888",
            "port": 8888,
            "is_external": False,
            "open_in_new_tab": True,
            "requires_auth": True,
            "requires_approval": True,
            "sort_order": 1
        },
        {
            "name": "vscode_server",
            "display_name": "VS Code Server",
            "description": "Visual Studio Code in the browser",
            "category_id": dev_cat.id if dev_cat else None,
            "icon": "code",
            "url": "http://localhost:8080",
            "port": 8080,
            "is_external": False,
            "open_in_new_tab": True,
            "requires_auth": True,
            "requires_approval": True,
            "sort_order": 2
        },
        {
            "name": "chatgpt",
            "display_name": "ChatGPT",
            "description": "OpenAI ChatGPT interface",
            "category_id": ai_cat.id if ai_cat else None,
            "icon": "chat",
            "url": "https://chat.openai.com",
            "is_external": True,
            "open_in_new_tab": True,
            "requires_auth": False,
            "requires_approval": True,
            "sort_order": 1
        }
    ]
    
    created_count = 0
    for service_data in services:
        existing = db.query(Service).filter(Service.name == service_data["name"]).first()
        if not existing:
            service = Service(**service_data)
            db.add(service)
            created_count += 1
    
    db.commit()
    logger.info(f"Created {created_count} default services")

async def create_admin_user(db):
    """Create default admin user"""
    admin_email = "admin@example.com"
    admin_password = "admin123"
    
    # Check if admin exists
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        logger.info(f"Admin user already exists: {admin_email}")
        return
    
    # Create admin user
    admin_user = User(
        real_name="System Administrator",
        display_name="Admin",
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        department="IT",
        position="System Administrator",
        is_active=True,
        is_admin=True,
        approval_status='approved',
        approved_at=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.commit()
    
    logger.info(f"Created admin user: {admin_email} (password: {admin_password})")

async def main():
    """Main initialization function"""
    logger.info("🚀 Starting system initialization...")
    
    try:
        await init_db()
        logger.info("✅ Database tables created")
        
        db = SessionLocal()
        try:
            await create_default_permissions(db)
            await create_default_features(db)
            await create_default_roles(db)
            await create_default_groups(db)
            await create_service_categories(db)
            await create_default_services(db)
            await create_admin_user(db)
            
            logger.info("🎉 System initialization completed!")
            
            # Print summary
            print("\n" + "="*60)
            print("CENTRAL AUTHENTICATION SYSTEM - INITIALIZATION COMPLETE")
            print("="*60)
            print(f"Database URL: {os.getenv('DATABASE_URL', 'Not configured')}")
            print(f"Admin Email: {os.getenv('ADMIN_EMAIL', 'admin@example.com')}")
            print(f"Admin Password: {os.getenv('ADMIN_PASSWORD', 'admin123')}")
            print(f"Server Port: {os.getenv('PORT', '8001')}")
            print("\nNext steps:")
            print("1. Start the server: python -m app.main")
            print("2. Access the API docs: http://localhost:8001/docs")
            print("3. Login with admin credentials")
            print("4. Change the default admin password")
            print("="*60)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 