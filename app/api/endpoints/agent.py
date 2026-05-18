from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_sync_db
from app.core.security import allow_authenticated
from app.models.agent import ProjectPhase, AgentRun, TestCase, TestReport
from app.schemas.agent import (
    ProjectPhaseCreate, ProjectPhasePatch, ProjectPhaseResponse,
    AgentRunCreate, AgentRunPatch, AgentRunResponse,
    TestCaseCreate, TestCaseResponse,
    TestReportCreate, TestReportResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Project Phases
# ---------------------------------------------------------------------------

@router.post("/project-phases", response_model=ProjectPhaseResponse, tags=["agent"])
def create_project_phase(
    payload: ProjectPhaseCreate,
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    phase = ProjectPhase(**payload.model_dump())
    db.add(phase)
    db.commit()
    db.refresh(phase)
    return phase


@router.get("/project-phases", response_model=List[ProjectPhaseResponse], tags=["agent"])
def list_project_phases(
    project_id: int = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    q = select(ProjectPhase).where(
        ProjectPhase.project_id == project_id,
        ProjectPhase.is_deleted == False,
    )
    if status:
        q = q.where(ProjectPhase.status == status)
    q = q.order_by(ProjectPhase.id.desc())
    return db.execute(q).scalars().all()


@router.patch("/project-phases/{phase_id}", response_model=ProjectPhaseResponse, tags=["agent"])
def patch_project_phase(
    phase_id: int,
    payload: ProjectPhasePatch,
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    phase = db.get(ProjectPhase, phase_id)
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(phase, k, v)
    db.commit()
    db.refresh(phase)
    return phase


# ---------------------------------------------------------------------------
# Agent Runs
# ---------------------------------------------------------------------------

@router.post("/agent-runs", response_model=AgentRunResponse, tags=["agent"])
def create_agent_run(
    payload: AgentRunCreate,
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    run = AgentRun(**payload.model_dump())
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.get("/agent-runs", response_model=List[AgentRunResponse], tags=["agent"])
def list_agent_runs(
    project_id: int = Query(...),
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    q = select(AgentRun).where(
        AgentRun.project_id == project_id,
        AgentRun.is_deleted == False,
    ).order_by(AgentRun.id.desc())
    return db.execute(q).scalars().all()


@router.patch("/agent-runs/{run_id}", response_model=AgentRunResponse, tags=["agent"])
def patch_agent_run(
    run_id: int,
    payload: AgentRunPatch,
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    run = db.get(AgentRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(run, k, v)
    if payload.status in ("completed", "failed"):
        run.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(run)
    return run


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

@router.post("/test-cases", response_model=TestCaseResponse, tags=["agent"])
def create_test_case(
    payload: TestCaseCreate,
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    tc = TestCase(**payload.model_dump())
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


@router.get("/test-cases", response_model=List[TestCaseResponse], tags=["agent"])
def list_test_cases(
    project_id: int = Query(...),
    environment: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    q = select(TestCase).where(
        TestCase.project_id == project_id,
        TestCase.is_deleted == False,
    )
    if environment:
        q = q.where(TestCase.environment == environment)
    if type:
        q = q.where(TestCase.type == type)
    return db.execute(q).scalars().all()


# ---------------------------------------------------------------------------
# Test Reports
# ---------------------------------------------------------------------------

@router.post("/test-reports", response_model=TestReportResponse, tags=["agent"])
def create_test_report(
    payload: TestReportCreate,
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    report = TestReport(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/test-reports", response_model=List[TestReportResponse], tags=["agent"])
def list_test_reports(
    project_id: int = Query(...),
    environment: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db),
    _: object = Depends(allow_authenticated),
):
    q = select(TestReport).where(
        TestReport.project_id == project_id,
        TestReport.is_deleted == False,
    )
    if environment:
        q = q.where(TestReport.environment == environment)
    return db.execute(q).scalars().all()
