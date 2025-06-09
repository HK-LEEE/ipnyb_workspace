from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from ..database import Base

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # UUID 기반 사용자 참조
    owner_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
    
    # 워크스페이스 설정
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Jupyter 설정
    jupyter_port = Column(Integer, nullable=True)
    jupyter_token = Column(String(255), nullable=True)
    jupyter_status = Column(String(20), default="stopped")  # stopped, starting, running, error
    
    # 파일 시스템 정보
    path = Column(String(500), nullable=True)  # workspace_path에서 path로 변경
    max_storage_mb = Column(Integer, default=1000)
    
    # 시스템 정보
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_accessed = Column(DateTime, nullable=True)
    
    # 관계 정의
    owner = relationship("User", back_populates="workspaces") 