from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.template import ProjectTemplate, TemplateTask
from app.schemas.template import ProjectTemplateCreate, ProjectTemplateUpdate


def _template_query():
    return (
        select(ProjectTemplate)
        .options(
            selectinload(ProjectTemplate.tasks),
            selectinload(ProjectTemplate.created_by),
        )
        .where(ProjectTemplate.is_deleted == False)
    )


def get_templates(db: Session) -> List[ProjectTemplate]:
    result = db.execute(_template_query().order_by(ProjectTemplate.name))
    return result.scalars().all()


def get_template(db: Session, template_id: int) -> Optional[ProjectTemplate]:
    result = db.execute(
        _template_query().where(ProjectTemplate.id == template_id)
    )
    return result.scalar_one_or_none()


def create_template(
    db: Session,
    data: ProjectTemplateCreate,
    created_by_id: Optional[int] = None,
) -> ProjectTemplate:
    from app.utils.ids import generate_public_id
    
    existing = db.execute(select(ProjectTemplate).where(ProjectTemplate.name == data.name, ProjectTemplate.is_deleted == False)).scalar_one_or_none()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"A template with name '{data.name}' already exists.")
    db_template = ProjectTemplate(
        public_id     = generate_public_id("TPL-"),
        name          = data.name,
        description   = data.description,
        billing_type  = data.billing_type,
        is_public     = data.is_public,
        created_by_id = created_by_id,
    )
    db.add(db_template)
    db.flush()

    for i, t in enumerate(data.tasks):
        db.add(TemplateTask(
            template_id     = db_template.id,
            title           = t.title,
            description     = t.description,
            estimated_hours = t.estimated_hours,
            duration        = t.duration,
            billing_type    = t.billing_type,
            tags            = t.tags,
            order_index     = t.order_index if t.order_index else i,
        ))

    db.commit()
    return get_template(db, db_template.id)


def update_template(
    db: Session,
    template_id: int,
    data: ProjectTemplateUpdate,
) -> Optional[ProjectTemplate]:
    template = db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        return None

    if data.name is not None and data.name != template.name:
        existing = db.execute(select(ProjectTemplate).where(ProjectTemplate.name == data.name, ProjectTemplate.id != template_id, ProjectTemplate.is_deleted == False)).scalar_one_or_none()
        if existing:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"A template with name '{data.name}' already exists.")
        template.name = data.name
    if data.description is not None:
        template.description = data.description
    if data.billing_type is not None:
        template.billing_type = data.billing_type
    if data.is_public is not None:
        template.is_public = data.is_public


    if data.tasks is not None:

        existing = db.execute(
            select(TemplateTask).where(TemplateTask.template_id == template_id)
        ).scalars().all()
        for t in existing:
            db.delete(t)
        db.flush()


        for i, t in enumerate(data.tasks):
            db.add(TemplateTask(
                template_id     = template_id,
                title           = t.title,
                description     = t.description,
                estimated_hours = t.estimated_hours,
                duration        = t.duration,
                billing_type    = t.billing_type,
                tags            = t.tags,
                order_index     = t.order_index if t.order_index else i,
            ))

    db.commit()
    return get_template(db, template_id)


def add_template_task(
    db: Session,
    template_id: int,
    task_data: dict,
) -> Optional[ProjectTemplate]:
    template = db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        return None


    max_idx = db.execute(
        select(TemplateTask.order_index)
        .where(TemplateTask.template_id == template_id)
        .order_by(TemplateTask.order_index.desc())
        .limit(1)
    ).scalar() or 0

    db.add(TemplateTask(
        template_id     = template_id,
        title           = task_data["title"],
        description     = task_data.get("description"),
        estimated_hours = task_data.get("estimated_hours"),
        duration        = task_data.get("duration"),
        billing_type    = task_data.get("billing_type"),
        tags            = task_data.get("tags"),
        order_index     = max_idx + 1,
    ))
    db.commit()
    return get_template(db, template_id)


def remove_template_task(db: Session, template_id: int, task_id: int) -> Optional[ProjectTemplate]:
    task = db.execute(
        select(TemplateTask).where(
            TemplateTask.id == task_id,
            TemplateTask.template_id == template_id,
        )
    ).scalar_one_or_none()
    if not task:
        return None
    db.delete(task)
    db.commit()
    return get_template(db, template_id)


def delete_template(db: Session, template_id: int) -> bool:
    template = db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        return False
    template.is_deleted = True
    db.commit()
    return True
