from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserBase
from app.schemas.masters import MasterResponse, MasterLookupResponse
from app.schemas.document import DocumentResponse
from app.schemas.base import BaseSchema


class ProjectMemberResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    user_id: int
    project_profile: Optional[str]  = None
    portal_profile: Optional[str]   = None
    role_in_project: Optional[str]  = None
    invitation_status_id: Optional[int] = None

    is_owner: bool                  = False
    created_at: Optional[datetime]  = None

    is_processed: bool                          = False
    previous_invitation_status_id: Optional[int] = None


    user: Optional[UserBase] = None


class ProjectMemberCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[int] = None
    user_email: Optional[str] = None
    project_profile: str = "Member"
    portal_profile: str = "User"


class ProjectMemberUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_profile: Optional[str]          = None
    portal_profile: Optional[str]           = None
    invitation_status_id: Optional[int]         = None
    is_owner: Optional[bool]                = None

    previous_invitation_status_id: Optional[int]   = None
    is_processed: Optional[bool]                = None


class ProjectCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_name: str       = Field(..., min_length=1)
    project_name: str       = Field(..., min_length=1)
    customer_name: str      = Field(..., min_length=1)
    project_id_sync: str    = Field(..., min_length=1)

    billing_model: str
    project_type: str

    expected_start_date: Optional[date] = None
    expected_end_date: Optional[date]   = None

    client_name: Optional[str]              = None
    description: Optional[str]              = None
    project_status_external: Optional[str]  = None
    tags: Optional[str]                     = None

    owner_id: Optional[int]                 = None
    project_manager_id: Optional[int]       = None
    project_manager_email: Optional[str]    = None
    delivery_head_id: Optional[int]         = None
    delivery_head_email: Optional[str]      = None
    template_id: Optional[int]              = None

    status_id: Optional[int]                = None
    priority_id: Optional[int]              = None


    estimated_hours: Optional[float]        = 0.0
    actual_hours: Optional[float]           = 0.0

    actual_start_date: Optional[date]       = None
    actual_end_date: Optional[date]         = None

    is_archived: bool                       = False
    is_template: bool                       = False
    is_group: bool                          = False

    user_emails: List[str]                  = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_name: Optional[str]       = None
    project_name: Optional[str]       = None
    customer_name: Optional[str]      = None
    project_id_sync: Optional[str]    = None
    client_name: Optional[str]        = None
    tags: Optional[str]               = None

    billing_model: Optional[str]   = None
    project_type: Optional[str]    = None
    project_status_external: Optional[str]  = None

    expected_start_date: Optional[date] = None
    expected_end_date: Optional[date]   = None

    owner_id: Optional[int]                 = None
    project_manager_id: Optional[int]       = None
    project_manager_email: Optional[str]    = None
    delivery_head_id: Optional[int]         = None
    delivery_head_email: Optional[str]      = None

    status_id: Optional[int]                = None
    priority_id: Optional[int]              = None

    description: Optional[str]              = None

    estimated_hours: Optional[float]        = None
    actual_hours: Optional[float]           = None
    actual_start_date: Optional[date]       = None
    actual_end_date: Optional[date]         = None

    is_archived: Optional[bool]             = None
    is_template: Optional[bool]             = None
    is_group: Optional[bool]                = None
    user_emails: Optional[List[str]]        = None

    previous_status_id: Optional[int]   = None
    is_processed: Optional[bool]        = None




class ProjectSyncUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id_sync: Optional[str] = None
    account_name: Optional[str]    = None
    customer_name: Optional[str]   = None
    project_name: Optional[str]    = None






class ProjectResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: Optional[str] = None
    project_id_sync: Optional[str] = None
    account_name: Optional[str] = None
    project_name: Optional[str] = None
    customer_name: Optional[str] = None
    client_name: Optional[str] = None
    tags: Optional[str]        = None

    billing_model: Optional[str] = None
    project_type: Optional[str] = None
    project_status_external: Optional[str] = None

    expected_start_date: Optional[date] = None
    expected_end_date: Optional[date]   = None

    description: Optional[str]          = None
    
    status_id: Optional[int]            = None
    priority_id: Optional[int]          = None

    status_master: Optional[MasterLookupResponse]     = None
    priority_master: Optional[MasterLookupResponse]   = None


    owner_id: Optional[int]             = None
    project_manager_id: Optional[int]   = None
    delivery_head_id: Optional[int]     = None
    template_id: Optional[int]          = None

    estimated_hours: Optional[float]    = 0.0
    actual_hours: Optional[float]       = 0.0
    actual_start_date: Optional[date]   = None
    actual_end_date: Optional[date]     = None

    is_archived: bool                   = False
    is_template: bool                   = False
    is_group: bool                      = False
    is_processed: bool                  = False

    previous_status_id: Optional[int]   = None



    owner: Optional[UserBase]           = None
    project_manager: Optional[UserBase] = None
    delivery_head: Optional[UserBase]   = None


    team_members: List[ProjectMemberResponse] = Field(default_factory=list)
    documents: List[DocumentResponse]         = Field(default_factory=list)

    task_count: int      = 0
    issue_count: int     = 0
    milestone_count: int = 0
    completion_percentage: int = 0

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    items: List[ProjectResponse]






class ProjectUserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str]          = None
    user_email: str
    display_name: Optional[str]     = None
    project_id: int
    project_profile: str            = "Member"
    portal_profile: str             = "User"
