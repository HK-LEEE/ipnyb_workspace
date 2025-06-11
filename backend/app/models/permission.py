from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .tables import user_permissions, user_features, role_permissions, role_features, group_permissions, group_features

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
    icon = Column(String(50), nullable=True)  # 아이콘 이름
    url_path = Column(String(200), nullable=True)  # 기능 URL 경로
    is_external = Column(Boolean, default=False)  # 외부 URL 여부
    open_in_new_tab = Column(Boolean, default=False)  # 새 탭에서 열기 여부
    auto_grant = Column(Boolean, default=False)  # If True, automatically granted to new users
    requires_approval = Column(Boolean, default=True)  # If True, requires admin approval
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", secondary=user_features, back_populates="features")
    roles = relationship("Role", secondary=role_features, back_populates="features")
    groups = relationship("Group", secondary=group_features, back_populates="features") 