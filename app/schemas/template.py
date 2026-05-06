from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field




class TemplateTaskCreate(BaseModel):
    title: str                       = Field(..., min_length=1, max_length=255)
    description: Optional[str]       = None
    estimated_hours: Optional[float] = None
    duration: Optional[int]          = None
    billing_type: Optional[str]      = None
    tags: Optional[str]              = None
    order_index: int                 = 0

    model_config = ConfigDict(from_attributes=True)


class TemplateTaskUpdate(BaseModel):
    title: Optional[str]             = None
    description: Optional[str]       = None
    estimated_hours: Optional[float] = None
    duration: Optional[int]          = None
    billing_type: Optional[str]      = None
    tags: Optional[str]              = None
    order_index: Optional[int]       = None

    model_config = ConfigDict(from_attributes=True)


class TemplateTaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]       = None
    estimated_hours: Optional[float] = None
    duration: Optional[int]          = None
    billing_type: Optional[str]      = None
    tags: Optional[str]              = None
    order_index: int

    model_config = ConfigDict(from_attributes=True)




class ProjectTemplateCreate(BaseModel):
    name: str                                     = Field(..., min_length=1, max_length=255)
    description: Optional[str]                    = None
    billing_type: Optional[str]                   = None
    is_public: bool                               = True
    tasks: List[TemplateTaskCreate]               = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProjectTemplateUpdate(BaseModel):
    name: Optional[str]             = None
    description: Optional[str]      = None
    billing_type: Optional[str]     = None
    is_public: Optional[bool]       = None
    tasks: Optional[List[TemplateTaskCreate]] = None

    model_config = ConfigDict(from_attributes=True)


class CreatorResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str]  = None
    email: Optional[str]      = None

    model_config = ConfigDict(from_attributes=True)


class ProjectTemplateResponse(BaseModel):
    id: int
    public_id: Optional[str] = None
    name: str
    description: Optional[str]        = None
    billing_type: Optional[str]       = None
    is_public: bool                   = True
    created_by: Optional[CreatorResponse] = None
    created_at: Optional[datetime]    = None
    updated_at: Optional[datetime]    = None
    tasks: List[TemplateTaskResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TemplateCloneRequest(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=255)
    include_milestones: bool = False

    model_config = ConfigDict(from_attributes=True)
