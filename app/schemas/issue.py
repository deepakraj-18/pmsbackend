from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserBase
from app.schemas.masters import MasterLookupResponse
from app.schemas.document import DocumentResponse
from app.schemas.milestone import MilestoneResponse
from app.schemas.base import BaseSchema


class IssueCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bug_name: str = Field(..., min_length=1)
    description: Optional[str] = None

    project_id: Optional[int] = None
    milestone_id: Optional[int] = None
    associated_team_id: Optional[int] = None
    assignee_id: Optional[int] = None
    reporter_id: Optional[int] = None

    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    severity_id: Optional[int] = None
    classification_id: Optional[int] = None
    reporter_email: Optional[str] = None
    follower_emails: List[str] = Field(default_factory=list)
    assignee_emails: List[str] = Field(default_factory=list)

    module: Optional[str] = None
    tags: Optional[str] = None
    flag: Optional[str] = None
    reproducible_flag: bool = True

    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    
    document_ids: Optional[List[int]] = Field(default_factory=list)


class IssueUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bug_name: Optional[str] = None
    description: Optional[str] = None

    project_id: Optional[int] = None
    associated_team_id: Optional[int] = None
    milestone_id: Optional[int] = None
    assignee_id: Optional[int] = None
    reporter_id: Optional[int] = None
    assignee_emails: Optional[List[str]] = None
    follower_emails: Optional[List[str]] = None

    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    severity_id: Optional[int] = None
    classification_id: Optional[int] = None

    module: Optional[str] = None
    tags: Optional[str] = None
    flag: Optional[str] = None
    reproducible_flag: Optional[bool] = None

    start_date: Optional[date] = None
    due_date: Optional[date] = None
    last_closed_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    estimated_hours: Optional[float] = None

    previous_status_id: Optional[int] = None
    is_processed: Optional[bool]      = None

    document_ids: Optional[List[int]] = Field(default_factory=list)


class ProjectMin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_name: Optional[str] = None
    customer_name: Optional[str] = None
    account_name: Optional[str] = None

class IssueResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: Optional[str] = None
    bug_name: Optional[str] = None
    description: Optional[str] = None

    project_id: Optional[int] = None
    project: Optional[ProjectMin] = None

    milestone_id: Optional[int] = None
    milestone: Optional[MilestoneResponse] = None
    associated_team_id: Optional[int]
    assignee_id: Optional[int]
    reporter_id: Optional[int]

    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    severity_id: Optional[int] = None
    classification_id: Optional[int] = None

    status_master: Optional[MasterLookupResponse] = None
    priority_master: Optional[MasterLookupResponse] = None
    severity_master: Optional[MasterLookupResponse] = None
    classification_master: Optional[MasterLookupResponse] = None
    status: Optional[dict] = None
    priority: Optional[dict] = None
    severity: Optional[dict] = None
    classification: Optional[dict] = None

    module: Optional[str] = None
    tags: Optional[str] = None
    flag: Optional[str] = None
    reproducible_flag: bool = True

    start_date: Optional[date] = None
    due_date: Optional[date] = None
    last_closed_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    estimated_hours: Optional[float] = None

    is_processed: bool                  = False
    previous_status_id: Optional[int]   = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    assignee: Optional[UserBase] = None
    reporter: Optional[UserBase] = None

    followers: List[UserBase] = Field(default_factory=list)
    assignees: List[UserBase] = Field(default_factory=list)
    documents: List[DocumentResponse] = Field(default_factory=list)


class IssueListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    items: List[IssueResponse]
