"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base user schema"""
    real_name: str
    display_name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    requested_permissions: Optional[List[int]] = []
    requested_features: Optional[List[int]] = []


class UserUpdate(BaseModel):
    """Schema for user update"""
    real_name: Optional[str] = None
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    bio: Optional[str] = None
    role_id: Optional[int] = None
    group_id: Optional[int] = None
    is_active: Optional[bool] = None
    approval_status: Optional[str] = None
    approval_note: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseSchema):
    """Schema for user response"""
    id: UUID
    real_name: str
    display_name: Optional[str]
    email: str
    phone_number: Optional[str]
    department: Optional[str]
    position: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_admin: bool
    is_verified: bool
    approval_status: str
    approval_note: Optional[str]
    approved_at: Optional[datetime]
    role_id: Optional[int]
    group_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    login_count: int


class UserWithRelations(UserResponse):
    role: Optional['RoleResponse'] = None
    group: Optional['GroupResponse'] = None
    permissions: List['PermissionResponse'] = []
    features: List['FeatureResponse'] = []
    workspaces: List['WorkspaceResponse'] = []


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []
    feature_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None
    feature_ids: Optional[List[int]] = None


class RoleResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime


class RoleWithRelations(RoleResponse):
    permissions: List['PermissionResponse'] = []
    features: List['FeatureResponse'] = []
    users: List[UserResponse] = []


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class GroupCreate(GroupBase):
    permission_ids: Optional[List[int]] = []
    feature_ids: Optional[List[int]] = []


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None
    feature_ids: Optional[List[int]] = None


class GroupResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    created_by: Optional[UUID]


class GroupWithRelations(GroupResponse):
    permissions: List['PermissionResponse'] = []
    features: List['FeatureResponse'] = []
    members: List[UserResponse] = []


class PermissionBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    category: str  # basic, workspace, file, jupyter, llm, admin
    is_active: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(BaseSchema):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    category: str
    is_active: bool


class FeatureBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    category: str  # core, analysis, utility, ai, reporting, collaboration, integration, admin
    icon: Optional[str] = None
    url_path: Optional[str] = None
    is_external: bool = False
    open_in_new_tab: bool = False
    auto_grant: bool = False
    requires_approval: bool = True
    is_active: bool = True


class FeatureCreate(FeatureBase):
    pass


class FeatureUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    url_path: Optional[str] = None
    is_external: Optional[bool] = None
    open_in_new_tab: Optional[bool] = None
    auto_grant: Optional[bool] = None
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None


class FeatureResponse(BaseSchema):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    category: str
    icon: Optional[str]
    url_path: Optional[str]
    is_external: bool
    open_in_new_tab: bool
    auto_grant: bool
    requires_approval: bool
    is_active: bool


class ServiceCategoryBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class ServiceCategoryCreate(ServiceCategoryBase):
    pass


class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceCategoryResponse(BaseSchema):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime


class ServiceBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    icon: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = None
    is_external: bool = False
    open_in_new_tab: bool = False
    requires_auth: bool = True
    requires_approval: bool = True
    sort_order: int = 0
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    icon: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = None
    is_external: Optional[bool] = None
    open_in_new_tab: Optional[bool] = None
    requires_auth: Optional[bool] = None
    requires_approval: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceResponse(BaseSchema):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    category_id: Optional[int]
    icon: Optional[str]
    url: Optional[str]
    port: Optional[int]
    is_external: bool
    open_in_new_tab: bool
    requires_auth: bool
    requires_approval: bool
    sort_order: int
    is_active: bool
    created_at: datetime
    created_by: Optional[UUID]


class ServiceWithCategory(ServiceResponse):
    category: Optional[ServiceCategoryResponse] = None


class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    jupyter_port: Optional[int] = None
    is_active: bool = True


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    jupyter_port: Optional[int] = None
    is_active: Optional[bool] = None


class WorkspaceResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    owner_id: UUID
    jupyter_port: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class WorkspaceWithOwner(WorkspaceResponse):
    owner: UserResponse


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    sub: Optional[str] = None  # User ID
    email: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    permissions: List[str] = []
    features: List[str] = []


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr
    phone_last_digits: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserApproval(BaseModel):
    approval_status: str  # approved, rejected
    approval_note: Optional[str] = None


class BulkPermissionUpdate(BaseModel):
    user_ids: List[UUID]
    permission_ids: List[int]
    action: str  # grant, revoke


class BulkFeatureUpdate(BaseModel):
    user_ids: List[UUID]
    feature_ids: List[int]
    action: str  # grant, revoke


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    pending_approvals: int
    total_workspaces: int
    active_services: int
    system_health: str


class UserStats(BaseModel):
    user_id: UUID
    login_count: int
    last_login_at: Optional[datetime]
    workspace_count: int
    active_features: int


class DashboardData(BaseModel):
    user: UserResponse
    available_features: List[FeatureResponse]
    available_services: List[ServiceWithCategory]
    recent_workspaces: List[WorkspaceResponse]
    system_stats: Optional[SystemStats] = None


class FileUpload(BaseModel):
    filename: str
    content_type: str
    size: int
    workspace_id: Optional[int] = None


class FileResponse(BaseModel):
    filename: str
    path: str
    size: int
    content_type: str
    created_at: datetime
    workspace_id: Optional[int]


class LLMRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    context: Optional[str] = None


class LLMResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    processing_time: float


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: datetime


class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    model: str
    created_at: datetime
    updated_at: datetime


class JupyterSession(BaseModel):
    session_id: str
    kernel_id: str
    workspace_id: int
    port: int
    status: str
    created_at: datetime


class JupyterKernelRequest(BaseModel):
    workspace_id: int
    kernel_name: Optional[str] = "python3"


UserWithRelations.model_rebuild()
RoleWithRelations.model_rebuild()
GroupWithRelations.model_rebuild() 