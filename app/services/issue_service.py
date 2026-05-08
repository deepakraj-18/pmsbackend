from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.issue import Issue
from app.models.document import Document
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate
from app.utils.ids import generate_public_id, get_next_sequence_id
from app.models.project import Project
from app.utils.audit_utils import capture_audit_details, write_audit


def _issue_query():
    from app.models.master import MasterLookup
    return (
        select(Issue)
        .options(
            selectinload(Issue.project),
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.assignees),
            selectinload(Issue.followers),
            selectinload(Issue.documents),
            selectinload(Issue.status_master),
            selectinload(Issue.severity_master),
            selectinload(Issue.classification_master),
        )
    )


def get_issue(db: Session, issue_id: int) -> Optional[Issue]:
    result = db.execute(_issue_query().where(Issue.id == issue_id))
    return result.scalar_one_or_none()


def get_issues(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status_ids: Optional[List[int]] = None,
    priority_ids: Optional[List[int]] = None,
    severity_ids: Optional[List[int]] = None,
    assignee_emails: Optional[List[str]] = None,
    search: Optional[str] = None,
) -> dict:
    stmt = _issue_query()

    if project_id is not None:
        stmt = stmt.where(Issue.project_id == project_id)

    if status_ids:
        stmt = stmt.where(Issue.status_id.in_(status_ids))

    if priority_ids:
        stmt = stmt.where(Issue.priority_id.in_(priority_ids))

    if severity_ids:
        stmt = stmt.where(Issue.severity_id.in_(severity_ids))

    if search:
        q = f"%{search}%"
        stmt = stmt.where(
            or_(Issue.bug_name.ilike(q), Issue.public_id.ilike(q))
        )

    if assignee_emails:
        stmt = stmt.join(User, User.id == Issue.assignee_id).where(
            User.email.in_(assignee_emails)
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (db.execute(count_stmt)).scalar() or 0
    items_result = db.execute(stmt.offset(skip).limit(limit))
    return {"total": total, "items": items_result.scalars().unique().all()}


def create_issue(
    db: Session,
    issue: IssueCreate,
    actor_id: Optional[str] = None,
    created_by_id: Optional[int] = None,
) -> Issue:
    project = None
    if issue.project_id:
        project = db.execute(select(Project).where(Project.id == issue.project_id)).scalar_one_or_none()
    
    project_name = project.project_name if project else ""
    public_id = get_next_sequence_id(db, Issue, project_name, issue.project_id, "I") if issue.project_id else generate_public_id("ISS-")
    
    db_issue = Issue(
        public_id          = public_id,
        bug_name           = issue.bug_name,
        description        = issue.description,
        project_id         = issue.project_id,
        associated_team_id = issue.associated_team_id,
        reporter_id        = issue.reporter_id,
        assignee_id        = issue.assignee_id,
        status_id          = issue.status_id,
        severity_id        = issue.severity_id,
        classification_id  = issue.classification_id,
        module             = issue.module,
        tags               = issue.tags,
        reproducible_flag  = issue.reproducible_flag,
        start_date         = issue.start_date,
        due_date           = issue.due_date,
        estimated_hours    = issue.estimated_hours,
    )


    if issue.reporter_email and not issue.reporter_id:
        r_user = db.execute(select(User).where(User.email == issue.reporter_email)).scalar_one_or_none()
        if r_user:
            db_issue.reporter_id = r_user.id

    if issue.follower_emails:
        followers = (
            db.execute(select(User).where(User.email.in_(issue.follower_emails)))
        ).scalars().all()
        db_issue.followers.extend(followers)

    if issue.assignee_emails:
        assignees = (
            db.execute(select(User).where(User.email.in_(issue.assignee_emails)))
        ).scalars().all()
        db_issue.assignees.extend(assignees)

    if issue.document_ids:
        from app.models.document import Document
        docs = db.execute(select(Document).where(Document.id.in_(issue.document_ids))).scalars().all()
        db_issue.documents.extend(docs)

    db.add(db_issue)
    db.flush()

    write_audit(
        db, actor_id, "CREATE", "issues",
        issue.project_id or db_issue.id, db_issue.id,
        [{"field_name": "bug_name", "old_value": None, "new_value": issue.bug_name}],
    )
    db.commit()
    return get_issue(db, db_issue.id)


def update_issue(
    db: Session,
    issue_id: int,
    issue_update: IssueUpdate,
    actor_id: Optional[str] = None,
) -> Optional[Issue]:
    result = db.execute(select(Issue).where(Issue.id == issue_id))
    db_issue = result.scalar_one_or_none()
    if not db_issue:
        return None

    update_data = issue_update.model_dump(
        exclude_unset=True,
        exclude={"assignee_emails", "follower_emails", "document_ids"},
    )

    if "status_id" in update_data and update_data["status_id"] != db_issue.status_id:
        update_data["previous_status_id"] = db_issue.status_id
        update_data["is_processed"] = False


    if "priority_id" in update_data and update_data["priority_id"] != db_issue.priority_id:
        update_data["is_processed"] = False

    if "severity_id" in update_data and update_data["severity_id"] != db_issue.severity_id:
        update_data["is_processed"] = False



    changes = capture_audit_details(db_issue, update_data)
    for key, value in update_data.items():
        setattr(db_issue, key, value)

  
    if issue_update.assignee_emails is not None:
        assignees = (
            db.execute(select(User).where(User.email.in_(issue_update.assignee_emails)))
        ).scalars().all()
        db_issue.assignees = list(assignees)

    if issue_update.follower_emails is not None:
        followers = (
            db.execute(select(User).where(User.email.in_(issue_update.follower_emails)))
        ).scalars().all()
        db_issue.followers = list(followers)

    if issue_update.document_ids is not None:
        from app.models.document import Document
        docs = db.execute(select(Document).where(Document.id.in_(issue_update.document_ids))).scalars().all()
        db_issue.documents = list(docs)

    db_issue.last_modified_time = datetime.now(timezone.utc)

    write_audit(
        db, actor_id, "UPDATE", "issues",
        db_issue.project_id or issue_id, issue_id, changes,
    )
    db.commit()
    return get_issue(db, issue_id)



def delete_issue(
    db: Session,
    issue_id: int,
    actor_id: Optional[str] = None,
) -> bool:
    result = db.execute(select(Issue).where(Issue.id == issue_id))
    db_issue = result.scalar_one_or_none()
    if not db_issue:
        return False
    write_audit(
        db, actor_id, "DELETE", "issues",
        db_issue.project_id or issue_id, issue_id,
        [{"field_name": "bug_name", "old_value": db_issue.bug_name, "new_value": None}],
    )
    db.delete(db_issue)
    db.commit()
    return True


def search_issues(
    db: Session,
    query: str,
    project_id: Optional[int] = None,
    limit: int = 20,
) -> List[Issue]:
    if not query:
        return []
    q = f"%{query}%"

    stmt = _issue_query().where(
        or_(Issue.bug_name.ilike(q), Issue.public_id.ilike(q))
    )
    if project_id:
        stmt = stmt.where(Issue.project_id == project_id)
    result = db.execute(stmt.limit(limit))
    return result.scalars().unique().all()
