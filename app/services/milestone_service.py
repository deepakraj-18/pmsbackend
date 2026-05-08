from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, case
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.milestone import Milestone
from app.models.task import Task
from app.models.issue import Issue
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate
from app.utils.ids import generate_public_id
from app.utils.audit_utils import capture_audit_details, write_audit
from sqlalchemy import func

def _milestone_query():
    return (
        select(Milestone)
        .options(
            selectinload(Milestone.project),
            selectinload(Milestone.owner),
        )
    )

def _enrich_milestone(db: Session, milestone: Milestone) -> Milestone:
    from app.models.master import MasterLookup
    from sqlalchemy import case

    task_count = db.execute(
        select(func.count()).where(Task.milestone_id == milestone.id, Task.is_deleted == False)
    ).scalar() or 0

    completed_task_count = db.execute(
        select(func.count()).where(
            Task.milestone_id == milestone.id, Task.is_deleted == False, Task.completion_percentage == 100
        )
    ).scalar() or 0

    issue_stats = db.execute(
        select(func.count(Issue.id)).where(Issue.milestone_id == milestone.id, Issue.is_deleted == False)
    ).scalar() or 0

    issue_count = issue_stats or 0
    total_pct = round((completed_task_count / task_count) * 100) if task_count > 0 else 0

    milestone.__dict__['task_count'] = task_count
    milestone.__dict__['issue_count'] = issue_count
    milestone.__dict__['completion_percentage'] = total_pct
    return milestone

def _batch_enrich_milestones(db: Session, milestones: List[Milestone]) -> None:
    if not milestones:
        return
    milestone_ids = [m.id for m in milestones]

    task_stats = db.execute(
        select(
            Task.milestone_id, 
            func.count(Task.id),
            func.sum(case((Task.completion_percentage == 100, 1), else_=0))
        ).where(Task.milestone_id.in_(milestone_ids), Task.is_deleted == False).group_by(Task.milestone_id)
    ).all()

    task_counts = {row[0]: row[1] for row in task_stats}
    task_completed_counts = {row[0]: row[2] or 0 for row in task_stats}

    issue_counts_dict = dict(db.execute(
        select(Issue.milestone_id, func.count(Issue.id))
        .where(Issue.milestone_id.in_(milestone_ids), Issue.is_deleted == False)
        .group_by(Issue.milestone_id)
    ).all())

    for m in milestones:
        t_count = task_counts.get(m.id, 0)
        t_completed = task_completed_counts.get(m.id, 0)
        i_count = issue_counts_dict.get(m.id, 0)
        
        m.__dict__['task_count'] = t_count
        m.__dict__['issue_count'] = i_count
        
        if t_count and t_count > 0:
            m.__dict__['completion_percentage'] = round((float(t_completed) / float(t_count)) * 100)
        else:
            m.__dict__['completion_percentage'] = 0


def get_milestone(db: Session, milestone_id: int) -> Optional[Milestone]:
    result = db.execute(_milestone_query().where(Milestone.id == milestone_id))
    ms = result.scalar_one_or_none()
    if ms: return _enrich_milestone(db, ms)
    return None

def get_milestones(
    db: Session,
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Milestone]:
    stmt = _milestone_query()
    if project_id:
        stmt = stmt.where(Milestone.project_id == project_id)
    result = db.execute(stmt.offset(skip).limit(limit))
    milestones = list(result.scalars().unique().all())
    _batch_enrich_milestones(db, milestones)
    return milestones

def create_milestone(
    db: Session,
    milestone: MilestoneCreate,
    actor_id: Optional[str] = None,
) -> Milestone:
    public_id = generate_public_id("MLS-")
    db_milestone = Milestone(
        public_id      = public_id,
        milestone_name = milestone.milestone_name,
        description    = milestone.description,
        start_date     = milestone.start_date,
        end_date       = milestone.end_date,
        project_id     = milestone.project_id,
        owner_id       = milestone.owner_id,
        status_id      = milestone.status_id,
        priority_id    = milestone.priority_id,
        flags          = milestone.flags,

        tags           = milestone.tags,

    )
    db.add(db_milestone)
    db.flush()

    write_audit(
        db, actor_id, "CREATE", "milestones",
        milestone.project_id or db_milestone.id, db_milestone.id,
        [{"field_name": "milestone_name", "old_value": None, "new_value": milestone.milestone_name}],
    )
    db.commit()
    return get_milestone(db, db_milestone.id)

def update_milestone(
    db: Session,
    milestone_id: int,
    milestone_update: MilestoneUpdate,
    actor_id: Optional[str] = None,
) -> Optional[Milestone]:
    result = db.execute(select(Milestone).where(Milestone.id == milestone_id))
    db_milestone = result.scalar_one_or_none()
    if not db_milestone:
        return None

    update_data = milestone_update.model_dump(exclude_unset=True)

    if "status_id" in update_data and update_data["status_id"] != db_milestone.status_id:
        update_data["previous_status_id"] = db_milestone.status_id
        update_data["is_processed"] = False

    if "priority_id" in update_data and update_data["priority_id"] != db_milestone.priority_id:
        update_data["is_processed"] = False



    changes = capture_audit_details(db_milestone, update_data)
    for key, value in update_data.items():
        setattr(db_milestone, key, value)

    write_audit(
        db, actor_id, "UPDATE", "milestones",
        db_milestone.project_id or milestone_id, milestone_id, changes,
    )
    db.commit()
    return get_milestone(db, milestone_id)


def delete_milestone(
    db: Session,
    milestone_id: int,
    actor_id: Optional[str] = None,
) -> bool:
    result = db.execute(select(Milestone).where(Milestone.id == milestone_id))
    db_milestone = result.scalar_one_or_none()
    if not db_milestone:
        return False
    write_audit(
        db, actor_id, "DELETE", "milestones",
        db_milestone.project_id or milestone_id, milestone_id,
        [{"field_name": "milestone_name", "old_value": db_milestone.milestone_name, "new_value": None}],
    )
    db.delete(db_milestone)
    db.commit()
    return True
