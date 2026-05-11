from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_sync_db
from app.core.security import (
    allow_authenticated,
    allow_team_lead_plus,
    allow_task_create,
    allow_task_view,
    allow_task_delete,
    check_task_owner_or_lead,
    is_employee_only,
)
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services import task_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_task_create),
):
    return task_service.create_task(
        db=db,
        task=task,
        actor_id=current_user.o365_id or str(current_user.id),
        created_by_id=current_user.id,
    )


@router.post("/bulk", response_model=List[TaskResponse])
def bulk_create_tasks(
    tasks: List[TaskCreate],
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_team_lead_plus),
):
    results = []
    for t in tasks:
        results.append(
            task_service.create_task(
                db=db,
                task=t,
                actor_id=current_user.o365_id or str(current_user.id),
                created_by_id=current_user.id,
            )
        )
    return results


@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str = Query(..., min_length=1),
    project_id: Optional[int] = Query(None),
    limit: int = 20,
    db: Session = Depends(get_sync_db),
):
    return task_service.search_tasks(db, query=q, project_id=project_id, limit=limit)


@router.get("/", response_model=TaskListResponse)
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    assignee_email: Optional[List[str]] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_task_view),
):

    if is_employee_only(current_user):
        assignee_email = [current_user.email]

    return task_service.get_tasks(
        db,
        skip=skip,
        limit=limit,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_emails=assignee_email,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(
    task_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    db_task = task_service.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if is_employee_only(current_user) and db_task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: you are not assigned to this task.",
        )
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_task_owner_or_lead),
):
    updated = task_service.update_task(
        db,
        task_id=task_id,
        task_update=task,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_task_delete),
):
    success = task_service.delete_task(
        db,
        task_id=task_id,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
