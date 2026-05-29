from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.timelog import TimeLog
from app.models.task import Task
from app.models.user import User
from app.schemas.timelog import TimeLogCreate, TimeLogUpdate
from app.utils.ids import generate_public_id, get_next_sequence_id
from app.models.project import Project
from app.utils.audit_utils import capture_audit_details, write_audit


def _timelog_query():
    return (
        select(TimeLog)
        .options(
            selectinload(TimeLog.user),
            selectinload(TimeLog.created_by),
            selectinload(TimeLog.project),
            selectinload(TimeLog.task).selectinload(Task.project),
            selectinload(TimeLog.issue),
        )
    )


def get_timelog(db: Session, timelog_id: int) -> Optional[TimeLog]:
    result = db.execute(_timelog_query().where(TimeLog.id == timelog_id))
    return result.scalar_one_or_none()


def get_timelogs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    task_id: Optional[int] = None,
    issue_id: Optional[int] = None,
    user_ids: Optional[List[int]] = None,
    current_user=None,
) -> List[TimeLog]:
    stmt = _timelog_query()

    if project_id:

        stmt = stmt.outerjoin(Task, TimeLog.task_id == Task.id).where(
            or_(TimeLog.project_id == project_id, Task.project_id == project_id)
        )
    if task_id:
        stmt = stmt.where(TimeLog.task_id == task_id)
    if issue_id:
        stmt = stmt.where(TimeLog.issue_id == issue_id)
    if user_ids:
        stmt = stmt.where(TimeLog.user_id.in_(user_ids))


    if current_user is not None:
        stmt = stmt.where(TimeLog.user_id == current_user.id)

    result = db.execute(stmt.order_by(TimeLog.id).offset(skip).limit(limit))
    return result.scalars().unique().all()


def create_timelog(
    db: Session,
    timelog: TimeLogCreate,
    actor_id: Optional[str] = None,
    created_by_id: Optional[int] = None,
) -> TimeLog:
    project = None
    if timelog.project_id:
        project = db.execute(select(Project).where(Project.id == timelog.project_id)).scalar_one_or_none()
        
    project_name = project.project_name if project else ""
    public_id = get_next_sequence_id(db, TimeLog, project_name, timelog.project_id, "TL", True) if timelog.project_id else generate_public_id("TL-")

    db_timelog = TimeLog(
        public_id       = public_id,
        user_id         = timelog.user_id,
        created_by_id   = created_by_id,
        project_id      = timelog.project_id,
        task_id         = timelog.task_id,
        issue_id        = timelog.issue_id,
        date            = timelog.date,
        daily_log_hours = timelog.daily_log_hours,
        time_period     = timelog.time_period,
        log_title       = timelog.log_title,
        notes           = timelog.notes,
        billing_type    = timelog.billing_type or "Billable",
        approval_status_id = timelog.approval_status_id,
        general_log     = timelog.general_log or False,

    )
    db.add(db_timelog)
    db.flush()

    write_audit(
        db, actor_id, "CREATE", "timelogs",
        timelog.project_id or db_timelog.id, db_timelog.id,
        [{
            "field_name": "daily_log_hours",
            "old_value": None,
            "new_value": f"{timelog.daily_log_hours}h on {timelog.date} — {timelog.log_title or timelog.notes or ''}",
        }],
    )
    db.commit()
    return get_timelog(db, db_timelog.id)


def update_timelog(
    db: Session,
    timelog_id: int,
    timelog_update: TimeLogUpdate,
    actor_id: Optional[str] = None,
) -> Optional[TimeLog]:
    result = db.execute(select(TimeLog).where(TimeLog.id == timelog_id))
    db_timelog = result.scalar_one_or_none()
    if not db_timelog:
        return None

    update_data = timelog_update.model_dump(exclude_unset=True)

    if "approval_status_id" in update_data and update_data["approval_status_id"] != db_timelog.approval_status_id:
        update_data["previous_approval_status_id"] = db_timelog.approval_status_id
        update_data["is_processed"] = False


    changes = capture_audit_details(db_timelog, update_data)
    for key, value in update_data.items():
        setattr(db_timelog, key, value)

    write_audit(
        db, actor_id, "UPDATE", "timelogs",
        db_timelog.project_id or timelog_id, timelog_id, changes,
    )
    db.commit()
    return get_timelog(db, timelog_id)



def delete_timelog(
    db: Session,
    timelog_id: int,
    actor_id: Optional[str] = None,
) -> bool:
    result = db.execute(select(TimeLog).where(TimeLog.id == timelog_id))
    db_timelog = result.scalar_one_or_none()
    if not db_timelog:
        return False
    write_audit(
        db, actor_id, "DELETE", "timelogs",
        db_timelog.project_id or timelog_id, timelog_id,
        [{"field_name": "daily_log_hours", "old_value": str(db_timelog.daily_log_hours), "new_value": None}],
    )
    db.delete(db_timelog)
    db.commit()
    return True


def create_timelogs_bulk(
    db: Session,
    timelogs: List[TimeLogCreate],
    actor_id: Optional[str] = None,
    created_by_id: Optional[int] = None,
) -> List[TimeLog]:
    db_logs = []
    for log in timelogs:
        if (log.daily_log_hours or 0) <= 0:
            continue
            
        project = None
        if log.project_id:
            project = db.execute(select(Project).where(Project.id == log.project_id)).scalar_one_or_none()
            
        project_name = project.project_name if project else ""
        public_id = get_next_sequence_id(db, TimeLog, project_name, log.project_id, "TL", True) if log.project_id else generate_public_id("TL-")

        db_log = TimeLog(
            public_id       = public_id,
            user_id         = log.user_id,
            created_by_id   = created_by_id,
            project_id      = log.project_id,
            task_id         = log.task_id,
            issue_id        = log.issue_id,
            date            = log.date,
            daily_log_hours = log.daily_log_hours,
            time_period     = log.time_period,
            log_title       = log.log_title,
            notes           = log.notes,
            billing_type    = log.billing_type or "Billable",
            approval_status_id = log.approval_status_id,
            general_log     = log.general_log or False,

        )
        db_logs.append(db_log)
        db.add(db_log)

    db.flush()
    db.commit()
    for db_log in db_logs:
        db.refresh(db_log)

    if actor_id and db_logs:
        write_audit(
            db, actor_id, "CREATE", "timelogs",
            db_logs[0].project_id or db_logs[0].id, db_logs[0].id,
            [{"field_name": "bulk_create", "old_value": None,
              "new_value": f"Bulk created {len(db_logs)} time logs"}],
        )

    return [get_timelog(db, lg.id) for lg in db_logs]
