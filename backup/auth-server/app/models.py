"""
SQLAlchemy models for Auth Server
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from .database import Base

# Generate UUID for users
def generate_user_id():
    """Generate user unique ID (UUID based)"""
    return str(uuid.uuid4())

# Association tables for many-to-many relationships
user_permissions = Table(
    'user_permissions', 
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

user_features = Table(
    'user_features', 
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('feature_id', Integer, ForeignKey('features.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

role_features = Table(
    'role_features',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True), 
    Column('feature_id', Integer, ForeignKey('features.id'), primary_key=True)
)

group_permissions = Table(
    'group_permissions',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

group_features = Table(
    'group_features',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('feature_id', Integer, ForeignKey('features.id'), primary_key=True)
)

user_service_permissions = Table(
    'user_service_permissions',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('service_id', Integer, ForeignKey('services.id'), primary_key=True),
    Column('granted_at', DateTime, default=func.now()),
    Column('granted_by', UUID(as_uuid=True), ForeignKey('users.id'))
)

# Core Models
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    features = relationship("Feature", secondary=role_features, back_populates="roles")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    members = relationship("User", back_populates="group")
    creator = relationship("User", foreign_keys=[created_by], post_update=True)
    permissions = relationship("Permission", secondary=group_permissions, back_populates="groups")
    features = relationship("Feature", secondary=group_features, back_populates="groups")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # basic, workspace, file, jupyter, llm, admin
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", secondary=user_permissions, back_populates="permissions")
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    groups = relationship("Group", secondary=group_permissions, back_populates="permissions")

class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # core, analysis, utility, ai, reporting, collaboration, integration, admin
    icon = Column(String(50), nullable=True)
    url_path = Column(String(200), nullable=True)
    is_external = Column(Boolean, default=False)
    open_in_new_tab = Column(Boolean, default=False)
    auto_grant = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", secondary=user_features, back_populates="features")
    roles = relationship("Role", secondary=role_features, back_populates="features")
    groups = relationship("Group", secondary=group_features, back_populates="features")

class User(Base):
    __tablename__ = "users"
    
    # UUID-based unique ID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User information
    real_name = Column(String(100), nullable=False, comment="Real user name")
    display_name = Column(String(50), nullable=True, comment="Display name (nickname)")
    
    # Login information
    email = Column(String(100), unique=True, index=True, nullable=False, comment="Login email")
    phone_number = Column(String(20), nullable=True, comment="Phone number")
    hashed_password = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, comment="Account active status")
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False, comment="Email verification status")
    approval_status = Column(String(20), default='pending', comment="Approval status: pending, approved, rejected")
    approval_note = Column(Text, nullable=True, comment="Approval/rejection reason")
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, comment="Approving admin")
    approved_at = Column(DateTime, nullable=True, comment="Approval datetime")
    
    # Role and group assignments
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True, comment="User role ID")
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True, comment="User group ID")
    
    # Additional information
    department = Column(String(100), nullable=True, comment="Department")
    position = Column(String(100), nullable=True, comment="Position")
    bio = Column(Text, nullable=True, comment="Biography")
    
    # System information
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, comment="Login count")
    
    # Relationships
    workspaces = relationship("Workspace", back_populates="owner")
    role = relationship("Role", back_populates="users")
    group = relationship("Group", back_populates="members")
    approver = relationship("User", foreign_keys=[approved_by], remote_side=[id], post_update=True)
    created_services = relationship("Service", back_populates="creator")
    
    # Permission and feature relationships
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    features = relationship("Feature", secondary=user_features, back_populates="features")
    services = relationship("Service", secondary=user_service_permissions)

class ServiceCategory(Base):
    __tablename__ = "service_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    services = relationship("Service", back_populates="category")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('service_categories.id'))
    icon = Column(String(50))
    url = Column(String(500))
    port = Column(Integer)
    is_external = Column(Boolean, default=False)
    open_in_new_tab = Column(Boolean, default=False)
    requires_auth = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    category = relationship("ServiceCategory", back_populates="services")
    creator = relationship("User", back_populates="created_services")
    authorized_users = relationship("User", secondary=user_service_permissions)

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    jupyter_port = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="workspaces")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    revoked = Column(Boolean, default=False)
    replaced_by_token = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User")

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None) 