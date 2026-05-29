from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.masters import Skill
from app.models.roles import Role
from app.schemas.user import UserCreate, UserUpdate
from app.utils.ids import generate_public_id
from app.utils.audit_utils import capture_audit_details, write_audit

def _user_query():
    return (
        select(User)
        .options(
            selectinload(User.role),
            selectinload(User.status),
            selectinload(User.skills),
            selectinload(User.manager),
        )
    )

def get_user(db: Session, user_id: int) -> Optional[User]:
    result = db.execute(_user_query().where(User.id == user_id))
    return result.scalar_one_or_none()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    result = db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role_ids: Optional[List[int]] = None,
) -> dict:
    stmt = _user_query()

    if search:
        q = f"%{search}%"
        stmt = stmt.where(
            or_(
                User.first_name.ilike(q),
                User.last_name.ilike(q),
                User.email.ilike(q),
                User.username.ilike(q),
                User.display_name.ilike(q),
            )
        )
    if role_ids:
        stmt = stmt.where(User.role_id.in_(role_ids))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (db.execute(count_stmt)).scalar() or 0
    data = (db.execute(stmt.order_by(User.id).offset(skip).limit(limit))).scalars().unique().all()
    return {"total": total, "data": data}

def create_user(
    db: Session,
    user: UserCreate,
    actor_id: Optional[str] = None,
) -> User:
    public_id = generate_public_id("USR-")
    db_user = User(
        public_id    = public_id,
        employee_id  = user.employee_id or generate_public_id("EMP-"),
        first_name   = user.first_name,
        last_name    = user.last_name,
        email        = user.email,
        username     = user.username or user.email.split("@")[0],
        o365_id      = user.o365_id,
        phone        = user.phone,
        job_title    = user.job_title,
        join_date    = user.join_date,
        role_id      = user.role_id,
        status_id    = user.status_id,
        manager_email = user.manager_email,
        display_name = user.display_name,
        gender       = user.gender,
        country      = user.country,
        state        = user.state,
        language     = user.language,
        timezone     = user.timezone,
    )

    if user.skill_ids:
        skills = (db.execute(select(Skill).where(Skill.id.in_(user.skill_ids)))).scalars().all()
        db_user.skills.extend(skills)

    db.add(db_user)
    db.flush()

    write_audit(
        db, actor_id, "CREATE", "users", db_user.id, db_user.id,
        [{"field_name": "email", "old_value": None, "new_value": user.email}],
    )
    db.commit()
    return get_user(db, db_user.id)

def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate,
    actor_id: Optional[str] = None,
) -> Optional[User]:
    result = db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    changes = capture_audit_details(db_user, update_data)

    skill_ids = update_data.pop("skill_ids", None)
    if skill_ids is not None:
        skills = (db.execute(select(Skill).where(Skill.id.in_(skill_ids)))).scalars().all()
        db_user.skills = list(skills)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    write_audit(db, actor_id, "UPDATE", "users", user_id, user_id, changes)
    db.commit()
    return get_user(db, user_id)

def delete_user(
    db: Session,
    user_id: int,
    actor_id: Optional[str] = None,
) -> bool:
    result = db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False
    write_audit(
        db, actor_id, "DELETE", "users", user_id, user_id,
        [{"field_name": "email", "old_value": db_user.email, "new_value": None}],
    )
    db.delete(db_user)
    db.commit()
    return True

def search_users(db: Session, query: str, limit: int = 20) -> List[User]:
    if not query:
        return []
    q = f"%{query}%"
    result = db.execute(
        _user_query().where(
            or_(
                User.first_name.ilike(q),
                User.last_name.ilike(q),
                User.email.ilike(q),
                User.username.ilike(q),
                User.display_name.ilike(q),
            )
        ).limit(limit)
    )
    return result.scalars().unique().all()

def upsert_o365_user(
    db: Session,
    o365_id: str,
    email: Optional[str],
    first_name: str,
    last_name: str,
    display_name: Optional[str] = None,
) -> User:
    if not o365_id:
        raise ValueError("o365_id is required for SSO upsert")


    user = (db.execute(select(User).where(User.o365_id == o365_id))).scalar_one_or_none()


    if not user and email:
        user = (db.execute(select(User).where(User.email == email.lower()))).scalar_one_or_none()

    if user:

        user.o365_id = o365_id
        user.is_synced = True
        

        if not user.role_id:
            default_role = (db.execute(select(Role).where(Role.name == "Employee"))).scalar_one_or_none()
            if default_role:
                user.role_id = default_role.id
        

        if not user.status_id:
            from app.models.masters import UserStatus
            default_status = (db.execute(select(UserStatus).where(UserStatus.name == "Active"))).scalar_one_or_none()
            if default_status:
                user.status_id = default_status.id

        if first_name is not None: user.first_name = first_name
        if last_name is not None: user.last_name = last_name
        if display_name is not None: user.display_name = display_name
        
        db.commit()
        db.refresh(user)
        return user


    if not email:
        raise ValueError("Email is required to create a new SSO user record.")

    default_role = (db.execute(select(Role).where(Role.name == "Employee"))).scalar_one_or_none()
    

    base_username = email.split("@")[0].lower().replace(".", "_")
    username = base_username
    counter = 1
    while (db.execute(select(User.id).where(User.username == username))).scalar_one_or_none():
        username = f"{base_username}_{counter}"
        counter += 1

    new_user = User(
        public_id    = generate_public_id("USR-"),
        employee_id  = generate_public_id("EMP-"),
        first_name   = first_name or email.split("@")[0],
        last_name    = last_name or "",
        email        = email.lower(),
        username     = username,
        display_name = display_name or f"{first_name} {last_name}".strip(),
        o365_id      = o365_id,
        is_synced    = True,
        is_external  = False,
        role_id      = default_role.id if default_role else None,
    )
    
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise e
        
    return new_user
