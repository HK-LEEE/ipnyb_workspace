from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
import uuid
from ..database import Base

# 다대다 관계를 위한 연결 테이블들 (UUID 기반으로 변경)
user_group_mapping = Table(
    'user_group_mapping',
    Base.metadata,
    Column('user_id', CHAR(36), ForeignKey('users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('joined_at', DateTime, default=func.now())
)

user_role_mapping = Table(
    'user_role_mapping',
    Base.metadata,
    Column('user_id', CHAR(36), ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=func.now())
)

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
    
    # 추가 정보
    department = Column(String(100), nullable=True, comment="부서")
    position = Column(String(100), nullable=True, comment="직책")
    bio = Column(Text, nullable=True, comment="자기소개")
    
    # 시스템 정보
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, comment="로그인 횟수")
    
    # 관계 정의
    workspaces = relationship("Workspace", back_populates="owner")
    groups = relationship("Group", secondary=user_group_mapping, back_populates="members")
    roles = relationship("Role", secondary=user_role_mapping, back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # UUID로 변경
    
    # 관계 정의
    members = relationship("User", secondary=user_group_mapping, back_populates="groups")
    creator = relationship("User", foreign_keys=[created_by])

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON 형태로 권한 저장
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # 관계 정의
    users = relationship("User", secondary=user_role_mapping, back_populates="roles") 