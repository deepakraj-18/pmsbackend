from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_sync_db
from app.core.security import allow_authenticated, allow_team_lead_plus, is_employee_only
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, IssueListResponse
from app.services import issue_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])


@router.post("/", response_model=IssueResponse, dependencies=[Depends(allow_team_lead_plus)])
def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_team_lead_plus),
):

    if not issue.reporter_id:
        issue.reporter_id = current_user.id
    return issue_service.create_issue(
        db=db,
        issue=issue,
        actor_id=current_user.o365_id or str(current_user.id),
        created_by_id=current_user.id,
    )


@router.post("/bulk", response_model=List[IssueResponse], dependencies=[Depends(allow_team_lead_plus)])
def bulk_create_issues(
    issues: List[IssueCreate],
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_team_lead_plus),
):
    results = []
    for i in issues:
        if not i.reporter_id:
            i.reporter_id = current_user.id
        results.append(
            issue_service.create_issue(
                db=db, issue=i,
                actor_id=current_user.o365_id or str(current_user.id),
                created_by_id=current_user.id,
            )
        )
    return results


@router.get("/search", response_model=List[IssueResponse])
def search_issues(
    q: str = Query(..., min_length=1),
    project_id: Optional[int] = Query(None),
    limit: int = 20,
    db: Session = Depends(get_sync_db),
):
    return issue_service.search_issues(db, query=q, project_id=project_id, limit=limit)


@router.get("/", response_model=IssueListResponse)
def read_issues(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status_id: Optional[List[int]] = Query(None),
    priority_id: Optional[List[int]] = Query(None),
    severity_id: Optional[List[int]] = Query(None),
    assignee_email: Optional[List[str]] = Query(None),
    search: Optional[str] = None,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):

    if is_employee_only(current_user):
        assignee_email = [current_user.email]

    return issue_service.get_issues(
        db,
        skip=skip,
        limit=limit,
        project_id=project_id,
        status_ids=status_id,
        priority_ids=priority_id,
        severity_ids=severity_id,
        assignee_emails=assignee_email,
        search=search,
    )


@router.get("/{issue_id}", response_model=IssueResponse)
def read_issue(
    issue_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    db_issue = issue_service.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    if is_employee_only(current_user) and db_issue.assignee_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: you are not assigned to this issue.",
        )
    return db_issue


@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue: IssueUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    db_issue = issue_service.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    if is_employee_only(current_user) and db_issue.assignee_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: you can only update issues assigned to you.",
        )
    updated = issue_service.update_issue(
        db,
        issue_id=issue_id,
        issue_update=issue,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated


@router.delete("/{issue_id}", status_code=204, dependencies=[Depends(allow_team_lead_plus)])
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_team_lead_plus),
):
    success = issue_service.delete_issue(
        db,
        issue_id=issue_id,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")
