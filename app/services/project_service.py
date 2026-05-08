from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, or_, select, case
from sqlalchemy.orm import Session, selectinload

from app.models.project import Project, ProjectMember
from app.models.user import User
from app.models.task import Task
from app.models.issue import Issue
from app.models.milestone import Milestone
from app.models.template import ProjectTemplate, TemplateTask
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectSyncUpdate
from app.utils.ids import generate_public_id, get_next_project_id
from app.utils.audit_utils import capture_audit_details, write_audit






def _project_query_options():
    return [
        selectinload(Project.owner).selectinload(User.role),
        selectinload(Project.project_manager).selectinload(User.role),
        selectinload(Project.delivery_head).selectinload(User.role),
        selectinload(Project.source_template),
        selectinload(Project.team_members).selectinload(ProjectMember.user).selectinload(User.role),
        selectinload(Project.status_master),
        selectinload(Project.priority_master),
    ]

def _project_query(extra_options=()):
    return select(Project).options(*_project_query_options(), *extra_options)


def _compute_counts(db: Session, project_id: int) -> dict:
    
    task_count = db.execute(
        select(func.count()).where(Task.project_id == project_id, Task.is_deleted == False)
    ).scalar() or 0
    
    avg_completion = db.execute(
        select(func.avg(Task.completion_percentage)).where(
            Task.project_id == project_id, Task.is_deleted == False
        )
    ).scalar() or 0
    
    completed_task_count = db.execute(
        select(func.count()).where(Task.project_id == project_id, Task.is_deleted == False, Task.completion_percentage == 100)
    ).scalar() or 0

    issue_count = db.execute(
        select(func.count()).where(Issue.project_id == project_id, Issue.is_deleted == False)
    ).scalar() or 0
    milestone_count = db.execute(
        select(func.count()).where(Milestone.project_id == project_id, Milestone.is_deleted == False)
    ).scalar() or 0
    return {
        "task_count": task_count,
        "issue_count": issue_count,
        "milestone_count": milestone_count,
        "completion_percentage": round((completed_task_count / task_count) * 100) if task_count > 0 else 0
    }


def _enrich_project(db: Session, project: Project) -> Project:
    
    counts = _compute_counts(db, project.id)
    project.__dict__.update(counts)
    return project

def _batch_enrich_projects(db: Session, projects: List[Project]) -> None:
    if not projects:
        return
    project_ids = [p.id for p in projects]
    
    task_stats = db.execute(
        select(
            Task.project_id, 
            func.count(Task.id),
            func.sum(case((Task.completion_percentage == 100, 1), else_=0))
        ).where(Task.project_id.in_(project_ids), Task.is_deleted == False).group_by(Task.project_id)
    ).all()
    
    task_counts = {row[0]: row[1] for row in task_stats}
    task_pcts = {row[0]: round((float(row[2] or 0) / float(row[1] or 1)) * 100) for row in task_stats}
    
    issue_counts = dict(db.execute(
        select(Issue.project_id, func.count()).where(Issue.project_id.in_(project_ids), Issue.is_deleted == False).group_by(Issue.project_id)
    ).all())
    
    milestone_counts = dict(db.execute(
        select(Milestone.project_id, func.count()).where(Milestone.project_id.in_(project_ids), Milestone.is_deleted == False).group_by(Milestone.project_id)
    ).all())
    
    for p in projects:
        p.__dict__.update({
            "task_count": task_counts.get(p.id, 0),
            "issue_count": issue_counts.get(p.id, 0),
            "milestone_count": milestone_counts.get(p.id, 0),
            "completion_percentage": task_pcts.get(p.id, 0),
        })







def get_project(db: Session, project_id: int) -> Optional[Project]:
    result = db.execute(
        _project_query().where(Project.id == project_id, Project.is_deleted == False)
    )
    project = result.scalar_one_or_none()
    if project:
        _enrich_project(db, project)
    return project


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_ids: Optional[List[int]] = None,
    priority_ids: Optional[List[int]] = None,
    manager_emails: Optional[List[str]] = None,
    is_archived: Optional[bool] = None,
    is_template: Optional[bool] = None,
    include_all: bool = False,
    search: Optional[str] = None,
    current_user=None,
) -> dict:
    stmt = select(Project).where(Project.is_deleted == False)

    if search:
        q = f"%{search}%"
        stmt = stmt.where(
            or_(
                Project.project_name.ilike(q),
                Project.public_id.ilike(q),
                Project.project_id_sync.ilike(q),
                Project.customer_name.ilike(q),
                Project.client_name.ilike(q),
            )
        )

    if status_ids:
        stmt = stmt.where(Project.status_id.in_(status_ids))
    if priority_ids:
        stmt = stmt.where(Project.priority_id.in_(priority_ids))

    if current_user is not None:
        stmt = stmt.join(ProjectMember, ProjectMember.project_id == Project.id).where(
            ProjectMember.user_id == current_user.id
        )

    if not include_all:
        if is_archived is not None:
            stmt = stmt.where(Project.is_archived == is_archived)
        if is_template is not None:
            stmt = stmt.where(Project.is_template == is_template)

    if manager_emails:
        stmt = (
            stmt.join(User, Project.project_manager_id == User.id)
            .where(User.email.in_(manager_emails))
        )

    # Count before adding pagination and eager loading
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    
    # Add eager loading and pagination
    stmt = stmt.options(*_project_query_options()).offset(skip).limit(limit)
    
    result = db.execute(stmt)
    projects = list(result.scalars().unique().all())
    _batch_enrich_projects(db, projects)
    return {"total": total, "items": projects}


def search_projects(
    db: Session,
    query: str,
    limit: int = 20,
) -> List[Project]:
    if not query:
        return []
    q = f"%{query}%"
    stmt = _project_query().where(
        Project.is_deleted == False,
        or_(
            Project.project_name.ilike(q),
            Project.public_id.ilike(q),
            Project.project_id_sync.ilike(q),
            Project.customer_name.ilike(q),
        ),
    ).limit(limit)
    result = db.execute(stmt)
    projects = list(result.scalars().unique().all())
    _batch_enrich_projects(db, projects)
    return projects






def create_project(
    db: Session,
    project: ProjectCreate,
    actor_id: str,
) -> Project:
    public_id = get_next_project_id(db, Project)

    pm_id = project.project_manager_id
    if project.project_manager_email:
        pm_user = db.execute(select(User).where(User.email == project.project_manager_email)).scalar_one_or_none()
        if pm_user:
            pm_id = pm_user.id

    dh_id = project.delivery_head_id
    if project.delivery_head_email:
        dh_user = db.execute(select(User).where(User.email == project.delivery_head_email)).scalar_one_or_none()
        if dh_user:
            dh_id = dh_user.id

    db_project = Project(
        public_id               = public_id,
        project_name            = project.project_name,
        account_name            = project.account_name,
        customer_name           = project.customer_name,
        client_name             = project.client_name,
        project_id_sync         = project.project_id_sync,
        description             = project.description,
        tags                    = project.tags,
        billing_model           = project.billing_model,
        project_type            = project.project_type,
        project_status_external = project.project_status_external,
        project_manager_id      = pm_id,
        delivery_head_id        = dh_id,
        owner_id                = project.owner_id,
        template_id             = project.template_id,
        status_id               = project.status_id,
        priority_id             = project.priority_id,

        expected_start_date     = project.expected_start_date,
        expected_end_date       = project.expected_end_date,
        estimated_hours         = project.estimated_hours or 0.0,
        actual_start_date       = project.actual_start_date,
        actual_end_date         = project.actual_end_date,
        actual_hours            = project.actual_hours or 0.0,
        is_archived             = project.is_archived,
        is_template             = project.is_template,
        is_group                = project.is_group,
    )

    db.add(db_project)
    db.flush()


    if project.template_id:
        clone_from_template(db, db_project.id, project.template_id)


    members_to_add = {}

    if project.user_emails:
        users_result = db.execute(select(User).where(User.email.in_(project.user_emails)))
        for u in users_result.scalars().all():
            members_to_add[u.id] = {"project_profile": "Member", "portal_profile": "User"}

    if project.owner_id:
        members_to_add[project.owner_id] = {"project_profile": "Project Lead", "portal_profile": "Administrator"}

    if pm_id:
        members_to_add[pm_id] = {"project_profile": "Project Manager", "portal_profile": "Administrator"}
        
    if dh_id:
        members_to_add[dh_id] = {"project_profile": "Delivery Head", "portal_profile": "Administrator"}

    for uid, profs in members_to_add.items():
        db.add(ProjectMember(
            project_id=db_project.id,
            user_id=uid,
            project_profile=profs["project_profile"],
            portal_profile=profs["portal_profile"],
        ))

    write_audit(
        db, actor_id, "CREATE", "projects", db_project.id, db_project.id,
        [{"field_name": "project_name", "old_value": None, "new_value": project.project_name}],
    )
    db.commit()
    return get_project(db, db_project.id)






def update_project(
    db: Session,
    project_id: int,
    project_update: ProjectUpdate,
    actor_id: Optional[str] = None,
) -> Optional[Project]:
    result = db.execute(select(Project).where(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        return None

    update_data = project_update.model_dump(
        exclude_unset=True,
        exclude={"user_emails", "project_manager_email", "delivery_head_email"},
    )

    if project_update.project_manager_email:
        pm_user = db.execute(
            select(User).where(User.email == project_update.project_manager_email)
        ).scalar_one_or_none()
        if pm_user:
            update_data["project_manager_id"] = pm_user.id

    if project_update.delivery_head_email:
        dh_user = db.execute(
            select(User).where(User.email == project_update.delivery_head_email)
        ).scalar_one_or_none()
        if dh_user:
            update_data["delivery_head_id"] = dh_user.id

    if "status_id" in update_data and update_data["status_id"] != db_project.status_id:
        update_data["previous_status_id"] = db_project.status_id
        update_data["is_processed"] = False

    if "priority_id" in update_data and update_data["priority_id"] != db_project.priority_id:
        update_data["is_processed"] = False

    changes = capture_audit_details(db_project, update_data)

    for key, value in update_data.items():
        setattr(db_project, key, value)


    if project_update.user_emails is not None:

        existing_members = db.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        ).scalars().all()
        existing_user_ids = {m.user_id for m in existing_members}


        new_users = db.execute(
            select(User).where(User.email.in_(project_update.user_emails))
        ).scalars().all()
        new_user_ids = {u.id for u in new_users}


        for u in new_users:
            if u.id not in existing_user_ids:
                db.add(ProjectMember(
                    project_id      = project_id,
                    user_id         = u.id,
                    project_profile = "Member",
                    portal_profile  = "User",
                    is_processed    = False,
                ))


        for m in existing_members:
            if m.user_id not in new_user_ids and m.user_id != db_project.owner_id:
                db.delete(m)

    roles_to_ensure = []
    if db_project.owner_id:
        roles_to_ensure.append({"uid": db_project.owner_id, "profile": "Project Lead", "portal": "Administrator", "is_owner": True})
    if db_project.project_manager_id:
        roles_to_ensure.append({"uid": db_project.project_manager_id, "profile": "Project Manager", "portal": "Administrator", "is_owner": False})
    if db_project.delivery_head_id:
        roles_to_ensure.append({"uid": db_project.delivery_head_id, "profile": "Delivery Head", "portal": "Administrator", "is_owner": False})

    for r in roles_to_ensure:
        existing = db.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == r["uid"])
        ).scalar_one_or_none()
        
        if not existing:
            db.add(ProjectMember(
                project_id      = project_id,
                user_id         = r["uid"],
                project_profile = r["profile"],
                portal_profile  = r["portal"],
                is_owner        = r["is_owner"],
                is_processed    = False
            ))
        else:
            if r["is_owner"]: 
                existing.is_owner = True
            if existing.project_profile == "Member" and r["profile"] != "Member":
                existing.project_profile = r["profile"]
                existing.portal_profile = r["portal"]

    write_audit(db, actor_id, "UPDATE", "projects", project_id, project_id, changes)
    db.commit()
    return get_project(db, project_id)


def delete_project(
    db: Session,
    project_id: int,
    actor_id: Optional[str] = None,
) -> bool:
    result = db.execute(select(Project).where(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        return False

    write_audit(
        db, actor_id, "DELETE", "projects", project_id, project_id,
        [{"field_name": "project_name", "old_value": db_project.project_name, "new_value": None}],
    )
    db_project.is_deleted = True
    db_project.is_active  = False
    db.commit()
    return True



def archive_project(
    db: Session,
    project_id: int,
    archived: bool = True,
    actor_id: Optional[str] = None,
) -> Optional[Project]:
    result = db.execute(select(Project).where(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        return None

    db_project.is_archived = archived
    write_audit(
        db, actor_id or "system", "UPDATE", "projects", project_id, project_id,
        [{"field_name": "is_archived", "old_value": str(not archived), "new_value": str(archived)}],
    )
    db.commit()
    return get_project(db, project_id)


def sync_project_fields(
    db: Session,
    project_id: int,
    sync_data: ProjectSyncUpdate,
    actor_id: Optional[str] = None,
) -> Optional[Project]:
    result = db.execute(select(Project).where(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        return None

    update_data = sync_data.model_dump(exclude_unset=True, exclude_none=True)
    changes = capture_audit_details(db_project, update_data)
    for key, value in update_data.items():
        setattr(db_project, key, value)

    write_audit(db, actor_id or "sync", "UPDATE", "projects", project_id, project_id, changes)
    db.commit()
    return get_project(db, project_id)


def add_project_member(
    db: Session,
    project_id: int,
    user_id: int,
    project_profile: str = "Member",
    portal_profile: str = "User",
) -> Optional[ProjectMember]:
    existing = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    member = ProjectMember(
        project_id      = project_id,
        user_id         = user_id,
        project_profile = project_profile,
        portal_profile  = portal_profile,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_project_member(
    db: Session,
    project_id: int,
    user_id: int,
    profile_data: dict,
) -> Optional[ProjectMember]:
    member = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).scalar_one_or_none()
    if not member:
        return None

    if "invitation_status_id" in profile_data and profile_data["invitation_status_id"] != member.invitation_status_id:
        member.previous_invitation_status_id = member.invitation_status_id
        member.is_processed = False

    for key, value in profile_data.items():
        if hasattr(member, key):
            setattr(member, key, value)
    
    db.commit()
    db.refresh(member)
    return member



def remove_project_member(
    db: Session,
    project_id: int,
    user_id: int,
    owner_id: Optional[int] = None,
) -> bool:
    
    if owner_id and user_id == owner_id:
        return False
    result = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).scalar_one_or_none()
    if not result:
        return False
    db.delete(result)
    db.commit()
    return True






def clone_from_template(
    db: Session,
    project_id: int,
    template_id: int,
) -> None:
    from app.utils.ids import get_next_sequence_id
    
    project = db.execute(select(Project).where(Project.id == project_id)).scalar_one_or_none()
    project_name = project.project_name if project else ""

    tmpl_tasks_result = db.execute(
        select(TemplateTask)
        .where(TemplateTask.template_id == template_id)
        .order_by(TemplateTask.order_index)
    )
    
    tasks_to_add = tmpl_tasks_result.scalars().all()
    for tt in tasks_to_add:
        pid = get_next_sequence_id(db, Task, project_name, project_id, "T")
        db.add(Task(
            public_id       = pid,
            task_name       = tt.title,
            description     = tt.description,
            project_id      = project_id,
            estimated_hours = tt.estimated_hours,
            duration        = tt.duration,
            billing_type    = tt.billing_type or "Billable",
            tags            = tt.tags,
        ))
        db.flush()
    db.commit()

