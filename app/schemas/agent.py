from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# ProjectPhase
# ---------------------------------------------------------------------------

class ProjectPhaseCreate(BaseModel):
    project_id: int
    phase: str
    status: str = "active"


class ProjectPhasePatch(BaseModel):
    status: Optional[str] = None
    phase: Optional[str] = None


class ProjectPhaseResponse(BaseModel):
    id: int
    project_id: int
    phase: str
    status: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# AgentRun
# ---------------------------------------------------------------------------

class AgentRunCreate(BaseModel):
    project_id: int
    agent_type: str
    model_used: Optional[str] = None
    phase_id: Optional[int] = None
    status: str = "running"


class AgentRunPatch(BaseModel):
    status: Optional[str] = None
    output_doc_path: Optional[str] = None
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None


class AgentRunResponse(BaseModel):
    id: int
    project_id: int
    agent_type: str
    model_used: Optional[str] = None
    phase_id: Optional[int] = None
    status: str
    output_doc_path: Optional[str] = None
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# TestCase
# ---------------------------------------------------------------------------

class TestCaseCreate(BaseModel):
    project_id: int
    task_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    type: Optional[str] = "e2e"
    environment: Optional[str] = None
    priority: Optional[str] = "Medium"
    created_by_agent: Optional[str] = None


class TestCaseResponse(BaseModel):
    id: int
    project_id: int
    task_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    type: Optional[str] = None
    environment: Optional[str] = None
    priority: Optional[str] = None
    created_by_agent: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# TestReport
# ---------------------------------------------------------------------------

class TestReportCreate(BaseModel):
    project_id: int
    test_case_id: Optional[int] = None
    environment: Optional[str] = None
    result: str = "pending"
    notes: Optional[str] = None
    executed_by_agent: Optional[str] = None


class TestReportResponse(BaseModel):
    id: int
    project_id: int
    test_case_id: Optional[int] = None
    environment: Optional[str] = None
    result: str
    notes: Optional[str] = None
    executed_by_agent: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
