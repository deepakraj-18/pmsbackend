from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.task_list import TaskList
from app.schemas.task_list import TaskListCreate, TaskListUpdate
from app.utils.audit_utils import capture_audit_details, write_audit

def _tl_query():
    return select(TaskList).where(TaskList.is_deleted == False).options(
        selectinload(TaskList.project),
        selectinload(TaskList.milestone),
    )

def get_task_list(db: Session, task_list_id: int) -> Optional[TaskList]:
    result = db.execute(_tl_query().where(TaskList.id == task_list_id))
    return result.scalar_one_or_none()

def get_task_lists(
    db: Session,
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[TaskList]:
    stmt = _tl_query()
    if project_id:
        stmt = stmt.where(TaskList.project_id == project_id)
    result = db.execute(stmt.order_by(TaskList.id).offset(skip).limit(limit))
    return result.scalars().unique().all()

def create_task_list(
    db: Session,
    task_list: TaskListCreate,
    actor_id: Optional[str] = None,
) -> TaskList:
    from sqlalchemy import func
    from fastapi import HTTPException
    
    clean_name = task_list.name.strip()
    
    stmt = select(TaskList).where(TaskList.name.ilike(clean_name))
    if task_list.project_id is not None:
        stmt = stmt.where(TaskList.project_id == task_list.project_id)
    else:
        stmt = stmt.where(TaskList.project_id.is_(None))
        
    existing = db.execute(stmt).scalars().first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"A task list named '{clean_name}' already exists in this project.")

    db_tl = TaskList(
        name         = clean_name,
        description  = task_list.description,
        project_id   = task_list.project_id,
        milestone_id = task_list.milestone_id,
    )
    db.add(db_tl)
    db.flush()

    write_audit(
        db, actor_id, "CREATE", "task_lists",
        task_list.project_id or db_tl.id, db_tl.id,
        [{"field_name": "name", "old_value": None, "new_value": clean_name}],
    )
    db.commit()
    return get_task_list(db, db_tl.id)

def get_or_create_general_list(db: Session, project_id: int) -> TaskList:
    from app.schemas.task_list import TaskListCreate
    from sqlalchemy import select
    
    stmt = select(TaskList).where(TaskList.name.ilike("General"), TaskList.project_id == project_id)
    existing = db.execute(stmt).scalars().first()
    if existing:
        return existing

    return create_task_list(
        db, 
        TaskListCreate(name="General", project_id=project_id, description="Default task list for general tasks")
    )

def update_task_list(
    db: Session,
    task_list_id: int,
    task_list_update: TaskListUpdate,
    actor_id: Optional[str] = None,
) -> Optional[TaskList]:
    result = db.execute(select(TaskList).where(TaskList.id == task_list_id))
    db_tl = result.scalar_one_or_none()
    if not db_tl:
        return None

    update_data = task_list_update.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        new_name = update_data["name"].strip()
        stmt = select(TaskList).where(
            TaskList.name.ilike(new_name),
            TaskList.project_id == db_tl.project_id,
            TaskList.id != task_list_id
        )
        conflict = db.execute(stmt).scalars().first()
        if conflict:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"A task list named '{new_name}' already exists in this project.")
        update_data["name"] = new_name

    changes = capture_audit_details(db_tl, update_data)
    
    milestone_changed = "milestone_id" in update_data and update_data["milestone_id"] != db_tl.milestone_id

    for k, v in update_data.items():
        setattr(db_tl, k, v)

    if milestone_changed:
        from app.models.task import Task
        from sqlalchemy import update
        db.execute(update(Task).where(Task.task_list_id == task_list_id).values(milestone_id=db_tl.milestone_id))

    write_audit(db, actor_id, "UPDATE", "task_lists", db_tl.project_id or task_list_id, task_list_id, changes)
    db.commit()
    return get_task_list(db, task_list_id)

def delete_task_list(
    db: Session,
    task_list_id: int,
    actor_id: Optional[str] = None,
) -> bool:
    result = db.execute(select(TaskList).where(TaskList.id == task_list_id))
    db_tl = result.scalar_one_or_none()
    if not db_tl:
        return False
    write_audit(
        db, actor_id, "DELETE", "task_lists",
        db_tl.project_id or task_list_id, task_list_id,
        [{"field_name": "name", "old_value": db_tl.name, "new_value": None}],
    )
    db.delete(db_tl)
    db.commit()
    return True

def search_task_lists(
    db: Session,
    query: str,
    project_id: Optional[int] = None,
    limit: int = 20,
) -> List[TaskList]:
    if not query:
        return []
    stmt = _tl_query().where(TaskList.name.ilike(f"%{query}%"))
    if project_id:
        stmt = stmt.where(TaskList.project_id == project_id)
    result = db.execute(stmt.limit(limit))
    return result.scalars().unique().all()
