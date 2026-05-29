from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project_group import ProjectGroup
from app.schemas.project_group import ProjectGroupCreate, ProjectGroupUpdate
from app.utils.audit_utils import write_audit, capture_audit_details

def get_project_group(db: Session, group_id: int):
    return db.query(ProjectGroup).filter(ProjectGroup.id == group_id).first()

def get_project_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProjectGroup).order_by(ProjectGroup.id).offset(skip).limit(limit).all()

def create_project_group(db: Session, group: ProjectGroupCreate, actor_id: Optional[str] = None):
    db_group = ProjectGroup(
        name=group.name,
        description=group.description
    )
    db.add(db_group)
    db.flush()

    write_audit(db, actor_id, "CREATE", "project_groups",
                resource_id=db_group.id,
                record_id=db_group.id,
                details=[{"field_name": "name", "old_value": None, "new_value": group.name}])

    db.commit()
    db.refresh(db_group)
    return db_group

def update_project_group(db: Session, group_id: int, group_update: ProjectGroupUpdate, actor_id: Optional[str] = None):
    db_group = get_project_group(db, group_id)
    if not db_group:
        return None

    update_data = group_update.model_dump(exclude_unset=True)
    changes = capture_audit_details(db_group, update_data)

    for key, value in update_data.items():
        setattr(db_group, key, value)

    write_audit(db, actor_id, "UPDATE", "project_groups",
                resource_id=group_id,
                record_id=group_id,
                details=changes)

    db.commit()
    db.refresh(db_group)
    return db_group

def delete_project_group(db: Session, group_id: int, actor_id: Optional[str] = None):
    db_group = get_project_group(db, group_id)
    if not db_group:
        return False

    write_audit(db, actor_id, "DELETE", "project_groups",
                resource_id=group_id,
                record_id=group_id,
                details=[{"field_name": "name", "old_value": db_group.name, "new_value": None}])

    db.delete(db_group)
    db.commit()
    return True

def search_project_groups(db: Session, query: str, limit: int = 20):
    if not query:
        return []
    q = f"%{query}%"
    return db.query(ProjectGroup).filter(ProjectGroup.name.ilike(q)).limit(limit).all()
