from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserBase
from app.schemas.masters import MasterLookupResponse
from app.schemas.base import BaseSchema

class TaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_name: str = Field(..., min_length=1)
    description: Optional[str] = None

    project_id: Optional[int]   = None
    task_list_id: Optional[int] = None
    milestone_id: Optional[int] = None
    associated_team_id: Optional[int] = None

    assignee_id: Optional[int]   = None
    owner_id: Optional[int]      = None

    status_id: Optional[int]   = None
    priority_id: Optional[int] = None
    tags: Optional[str]     = None

    start_date: Optional[date]      = None
    due_date: Optional[date]        = None
    duration: Optional[int]         = None
    completion_percentage: Optional[int] = 0

    estimated_hours: Optional[float] = None
    work_hours: Optional[float]      = 0.0
    billing_type: Optional[str]      = "Billable"

    owner_emails: List[str]    = Field(default_factory=list)
    assignee_emails: List[str] = Field(default_factory=list)

class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_name: Optional[str]            = None
    description: Optional[str]          = None
    project_id: Optional[int]           = None
    task_list_id: Optional[int]         = None
    milestone_id: Optional[int]         = None
    associated_team_id: Optional[int]   = None
    assignee_id: Optional[int]          = None
    owner_id: Optional[int]             = None
    status_id: Optional[int]            = None
    priority_id: Optional[int]          = None
    tags: Optional[str]                 = None
    start_date: Optional[date]          = None
    due_date: Optional[date]            = None
    completion_date: Optional[date]     = None
    duration: Optional[int]             = None
    completion_percentage: Optional[int]= None
    estimated_hours: Optional[float]    = None
    work_hours: Optional[float]         = None
    billing_type: Optional[str]         = None

    owner_emails: Optional[List[str]]    = None
    assignee_emails: Optional[List[str]] = None

    previous_status_id: Optional[int] = None
    is_processed: Optional[bool]      = None

class ProjectMin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_name: Optional[str] = None
    customer_name: Optional[str] = None
    account_name: Optional[str] = None

class TaskListMin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: Optional[str] = None

class MilestoneMin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    milestone_name: Optional[str] = None

class TaskResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: Optional[str] = None
    task_name: Optional[str] = None
    description: Optional[str] = None

    project_id: Optional[int] = None
    project: Optional[ProjectMin] = None

    task_list_id: Optional[int] = None
    task_list: Optional[TaskListMin] = None
    milestone_id: Optional[int] = None
    milestone: Optional[MilestoneMin] = None
    associated_team_id: Optional[int] = None

    assignee_id: Optional[int] = None
    owner_id: Optional[int] = None
    created_by_id: Optional[int] = None

    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    
    status_master: Optional[MasterLookupResponse] = None
    priority_master: Optional[MasterLookupResponse] = None
    

    status: Optional[dict] = None
    priority: Optional[dict] = None
    
    tags: Optional[str] = None

    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completion_date: Optional[date] = None
    duration: Optional[int] = None
    completion_percentage: Optional[int] = 0

    estimated_hours: Optional[float] = 0.0
    work_hours: Optional[float] = 0.0
    billing_type: Optional[str] = "Billable"

    is_processed: bool                  = False
    previous_status_id: Optional[int]   = None

    timelog_total: Optional[float] = 0.0
    difference: Optional[float] = 0.0

    assignee: Optional[UserBase]     = None
    single_owner: Optional[UserBase] = None
    creator: Optional[UserBase]      = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    team_name: Optional[str] = None

    owners: List[UserBase]    = Field(default_factory=list)
    assignees: List[UserBase] = Field(default_factory=list)

class TaskListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total: int
    items: List[TaskResponse]
