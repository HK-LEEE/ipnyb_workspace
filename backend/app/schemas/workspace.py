from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceResponse(WorkspaceBase):
    id: int
    path: str
    is_active: bool
    jupyter_port: Optional[int] = None
    jupyter_token: Optional[str] = None
    owner_id: str  # UUID 문자열
    created_at: datetime
    
    class Config:
        from_attributes = True 