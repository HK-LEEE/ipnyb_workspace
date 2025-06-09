from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
import uuid
from ..database import Base

def generate_user_id():
    """사용자 고유 ID 생성 (UUID 기반)"""
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    # UUID 기반 고유 ID
    id = Column(CHAR(36), primary_key=True, default=generate_user_id, index=True)
    
    # 실제 사용자 정보
    real_name = Column(String(100), nullable=False, comment="실제 사용자 이름")  # 실명
    display_name = Column(String(50), nullable=True, comment="표시될 이름 (닉네임)")  # 표시명/닉네임
    
    # 로그인 정보
    email = Column(String(100), unique=True, index=True, nullable=False, comment="로그인 이메일")
    phone_number = Column(String(20), nullable=True, comment="휴대폰 번호")
    hashed_password = Column(String(255), nullable=False)
    
    # 계정 상태
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False, comment="이메일 인증 여부")
    
    # 역할 및 그룹 (직접 참조로 변경)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True, comment="사용자 역할 ID")
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True, comment="사용자 그룹 ID")
    
    # 추가 정보
    department = Column(String(100), nullable=True, comment="부서")
    position = Column(String(100), nullable=True, comment="직책")
    bio = Column(Text, nullable=True, comment="자기소개")
    
    # 시스템 정보
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, comment="로그인 횟수")
    
    # 관계 정의 (직접 참조로 변경)
    workspaces = relationship("Workspace", back_populates="owner")
    role = relationship("Role", foreign_keys=[role_id], back_populates="users")
    group = relationship("Group", foreign_keys=[group_id], back_populates="members")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # UUID로 변경
    
    # 관계 정의 (1:N 관계로 변경)
    members = relationship("User", foreign_keys='User.group_id', back_populates="group")
    creator = relationship("User", foreign_keys=[created_by])

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON 형태로 권한 저장
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # 관계 정의 (1:N 관계로 변경)
    users = relationship("User", foreign_keys='User.role_id', back_populates="role") 