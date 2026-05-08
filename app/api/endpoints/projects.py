from __future__ import annotations

from typing import List, Optional
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_sync_db
from app.core.security import (
    allow_authenticated,
    allow_pm,
    allow_team_lead_plus,
    check_project_owner_or_pm,
    check_project_owner_or_lead,
    is_employee_only,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectSyncUpdate,
)
from app.schemas.task import TaskResponse, TaskListResponse
from app.schemas.issue import IssueResponse, IssueListResponse
from app.schemas.timelog import TimeLogResponse
from app.schemas.milestone import MilestoneResponse
from app.schemas.audit import AuditLogResponse
from app.schemas.template import TemplateCloneRequest, ProjectTemplateResponse
from app.services import project_service, task_service, issue_service, timelog_service, milestone_service
from app.services.template_cloning_service import TemplateCloningService

from app.services.teams_automation import create_ms_team_for_project

router = APIRouter(dependencies=[Depends(allow_authenticated)])






@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    project: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_pm),
):

    if not project.owner_id:
        project.owner_id = current_user.id

    db_project = project_service.create_project(
        db=db, project=project, actor_id=current_user.public_id
    )

    member_emails = project.user_emails or []
    def background_teams_worker(proj_name: str, emails: List[str], proj_id: int):
        from app.core.database import SessionLocal
        with SessionLocal() as db_session:
            from app.services.teams_automation import create_ms_team_for_project
            team_id = create_ms_team_for_project(proj_name, emails, proj_id)
            if team_id:
                proj = project_service.get_project(db_session, proj_id)
                if proj:
                    proj.ms_teams_group_id = team_id
                    db_session.commit()

    background_tasks.add_task(
        background_teams_worker,
        proj_name  = db_project.project_name,
        emails     = member_emails,
        proj_id    = db_project.id,
    )

    return db_project


@router.get("/check-sync-id")
def check_sync_id(
    id: str = Query(..., min_length=1),
    exclude_project_id: Optional[int] = Query(None),
    db: Session = Depends(get_sync_db),
):
    try:
        from sqlalchemy import select
        from app.models.project import Project

        stmt = select(Project.id).where(Project.project_id_sync == id)
        if exclude_project_id:
            stmt = stmt.where(Project.id != exclude_project_id)

        exists = db.execute(stmt).first() is not None
        return {"exists": exists}
    except Exception:
        logging.getLogger("app.projects").exception("check-sync-id failed for id=%s", id)
        raise HTTPException(status_code=503, detail="Unable to check sync ID availability. Please try again.")


@router.get("/check-name")
def check_name(
    name: str = Query(..., min_length=1),
    exclude_project_id: Optional[int] = Query(None),
    db: Session = Depends(get_sync_db),
):
    try:
        from sqlalchemy import select
        from app.models.project import Project

        stmt = select(Project.id).where(Project.project_name == name)
        if exclude_project_id:
            stmt = stmt.where(Project.id != exclude_project_id)

        exists = db.execute(stmt).first() is not None
        return {"exists": exists}
    except Exception:
        logging.getLogger("app.projects").exception("check-name failed for name=%s", name)
        raise HTTPException(status_code=503, detail="Unable to check name availability. Please try again.")


@router.get("/search", response_model=List[ProjectResponse])
def search_projects(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, gt=0, le=100),
    db: Session = Depends(get_sync_db),
):
    return project_service.search_projects(db, query=q, limit=limit)


@router.get("/", response_model=ProjectListResponse)
def read_projects(
    skip: int = 0,
    limit: int = 100,
    is_archived: Optional[bool] = Query(None),
    is_template: Optional[bool] = Query(None),
    include_all: bool = Query(True),
    status_id: Optional[List[int]] = Query(None),
    priority_id: Optional[List[int]] = Query(None),
    manager_emails: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    return project_service.get_projects(
        db,
        skip=skip,
        limit=limit,
        status_ids=status_id,
        priority_ids=priority_id,
        manager_emails=manager_emails,
        is_archived=is_archived,
        is_template=is_template,
        include_all=include_all,
        search=search,
        current_user=current_user if is_employee_only(current_user) else None,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")


    if is_employee_only(current_user):
        member_ids = {m.user_id for m in db_project.team_members}
        if current_user.id not in member_ids:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this project.",
            )
    return db_project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_project_owner_or_lead),
):
    db_project = project_service.update_project(
        db,
        project_id     = project_id,
        project_update = project,
        actor_id       = current_user.o365_id or str(current_user.id),
    )
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_project_owner_or_pm),
):
    success = project_service.delete_project(
        db,
        project_id = project_id,
        actor_id   = current_user.o365_id or str(current_user.id),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")


@router.patch("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_project_owner_or_pm),
):
    result = project_service.archive_project(
        db,
        project_id = project_id,
        archived   = True,
        actor_id   = current_user.o365_id or str(current_user.id),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.patch("/{project_id}/unarchive", response_model=ProjectResponse)
def unarchive_project(
    project_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_project_owner_or_pm),
):
    result = project_service.archive_project(
        db,
        project_id = project_id,
        archived   = False,
        actor_id   = current_user.o365_id or str(current_user.id),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.post("/{project_id}/sync", response_model=ProjectResponse)
def sync_project(
    project_id: int,
    sync_data: ProjectSyncUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_pm),
):
    result = project_service.sync_project_fields(
        db,
        project_id = project_id,
        sync_data  = sync_data,
        actor_id   = current_user.o365_id or str(current_user.id),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result






@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    
    db_project = project_service.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project.team_members


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    member: ProjectMemberCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_project_owner_or_pm),
):
    
    from app.models.user import User
    from sqlalchemy import select


    user = None
    if member.user_id:
        user = db.execute(select(User).where(User.id == member.user_id)).scalar_one_or_none()
    elif member.user_email:
        user = db.execute(select(User).where(User.email == member.user_email)).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = project_service.add_project_member(
        db,
        project_id      = project_id,
        user_id         = user.id,
        project_profile = member.project_profile,
        portal_profile  = member.portal_profile,
    )
    return result


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_project_owner_or_pm),
):
    
    db_project = project_service.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    success = project_service.remove_project_member(
        db,
        project_id = project_id,
        user_id    = user_id,
        owner_id   = db_project.owner_id,
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove this member. They may not be on the project or they are the project owner.",
        )






@router.get("/{project_id}/audit", response_model=List[AuditLogResponse])
def get_project_audit_logs(
    project_id: int,
    db: Session = Depends(get_sync_db),
):
    from sqlalchemy import select
    from app.models.audit import AuditLogs

    result = db.execute(
        select(AuditLogs)
        .where(
            AuditLogs.TableName == "projects",
            AuditLogs.Comments.like(f"%Record ID: {project_id}%"),
        )
        .order_by(AuditLogs.PerformedOn.desc())
    )
    return result.scalars().all()






@router.get("/{project_id}/dashboard")
def get_project_dashboard(
    project_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    

    db_project = project_service.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")


    from app.services.project_service import _compute_counts
    counts = _compute_counts(db, project_id)


    return {
        "project_id": project_id,
        "counts": counts
    }


@router.get("/{project_id}/tasks", response_model=TaskListResponse)
def get_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):

    return task_service.get_tasks(db, project_id=project_id, skip=skip, limit=limit)


@router.get("/{project_id}/issues", response_model=IssueListResponse)
def get_project_issues(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    return issue_service.get_issues(db, project_id=project_id, skip=skip, limit=limit)


@router.get("/{project_id}/timelogs", response_model=List[TimeLogResponse])
def get_project_timelogs(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    return timelog_service.get_timelogs(db, project_id=project_id, skip=skip, limit=limit)


@router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
def get_project_milestones(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    return milestone_service.get_milestones(db, project_id=project_id, skip=skip, limit=limit)


@router.post("/{project_id}/clone-to-template", response_model=ProjectTemplateResponse, status_code=status.HTTP_201_CREATED)
def clone_project_to_template(
    project_id: int,
    request: TemplateCloneRequest,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    new_template = TemplateCloningService.clone_project_to_template(
        db=db,
        project_id=project_id,
        request=request,
        user_id=current_user.id,
    )
    return new_template
