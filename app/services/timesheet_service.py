from typing import Optional
from sqlalchemy.orm import Session
from app.models.timesheet import Timesheet
from app.schemas.timesheet import TimesheetCreate, TimesheetUpdate
from app.utils.audit_utils import write_audit, capture_audit_details

def get_timesheets(db: Session, skip: int = 0, limit: int = 100, project_id: int = None, user_email: str = None):
    query = db.query(Timesheet)
    if project_id:
        query = query.filter(Timesheet.project_id == project_id)
    if user_email:
        query = query.filter(Timesheet.user_email == user_email)
    return query.order_by(Timesheet.id).offset(skip).limit(limit).all()

def get_timesheet(db: Session, timesheet_id: int):
    return db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()

def create_timesheet(db: Session, timesheet: TimesheetCreate, actor_id: Optional[str] = None):
    db_timesheet = Timesheet(
        name=timesheet.name,
        start_date=timesheet.start_date,
        end_date=timesheet.end_date,
        project_id=timesheet.project_id,
        user_email=timesheet.user_email,
        billing_type=timesheet.billing_type,
        total_hours=timesheet.total_hours,
        approval_status=timesheet.approval_status
    )
    db.add(db_timesheet)
    db.flush()

    write_audit(db, actor_id, "CREATE", "timesheets",
                resource_id=timesheet.project_id or db_timesheet.id,
                record_id=db_timesheet.id,
                details=[{"field_name": "name", "old_value": None, "new_value": timesheet.name}])

    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

def update_timesheet(db: Session, timesheet_id: int, timesheet_update: TimesheetUpdate, actor_id: Optional[str] = None):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        return None

    update_data = timesheet_update.model_dump(exclude_unset=True)
    changes = capture_audit_details(db_timesheet, update_data)

    for key, value in update_data.items():
        setattr(db_timesheet, key, value)

    write_audit(db, actor_id, "UPDATE", "timesheets",
                resource_id=db_timesheet.project_id or timesheet_id,
                record_id=timesheet_id,
                details=changes)

    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

def delete_timesheet(db: Session, timesheet_id: int, actor_id: Optional[str] = None):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        return False

    write_audit(db, actor_id, "DELETE", "timesheets",
                resource_id=db_timesheet.project_id or timesheet_id,
                record_id=timesheet_id,
                details=[{"field_name": "name", "old_value": db_timesheet.name, "new_value": None}])

    db.delete(db_timesheet)
    db.commit()
    return True
