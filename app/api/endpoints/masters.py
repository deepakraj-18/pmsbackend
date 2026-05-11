from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_sync_db
from app.core.security import allow_authenticated, allow_role_manage
from app.schemas.masters import MasterResponse, RoleResponse, SkillResponse, RoleCreate, RoleUpdate, MasterLookupResponse, BulkRolePermissionsUpdate
from app.schemas.user import RoleWithUsersResponse
from app.services import master_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])

@router.get("/lookups/{category}", response_model=List[MasterLookupResponse])
def read_master_lookups(category: str, db: Session = Depends(get_sync_db)):
    from app.models.master import MasterLookup
    from sqlalchemy import select
    result = db.execute(
        select(MasterLookup)
        .where(MasterLookup.category == category, MasterLookup.is_active == True)
        .order_by(MasterLookup.order_index, MasterLookup.id)
    )
    items = result.scalars().all()
    
    seen = set()
    unique_items = []
    for item in items:
        clean_label = item.label.strip().lower()
        if clean_label not in seen:
            unique_items.append(item)
            seen.add(clean_label)
    return unique_items

@router.get("/lookups/{category}/search", response_model=List[MasterLookupResponse])
def search_master_lookups(category: str, q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_sync_db)):
    from app.models.master import MasterLookup
    from sqlalchemy import select
    result = db.execute(
        select(MasterLookup)
        .where(MasterLookup.category == category, MasterLookup.is_active == True, MasterLookup.label.ilike(f"%{q}%"))
        .order_by(MasterLookup.order_index)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/user-statuses", response_model=List[MasterResponse])
def read_user_statuses(db: Session = Depends(get_sync_db)):
    return master_service.get_user_statuses(db)

@router.get("/user-statuses/search", response_model=List[MasterResponse])
def search_user_statuses(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_sync_db)):
    return master_service.search_user_statuses(db, q, limit)

@router.get("/statuses", response_model=List[MasterResponse])
def read_statuses(db: Session = Depends(get_sync_db)):
    return master_service.get_statuses(db)

@router.get("/statuses/search", response_model=List[MasterResponse])
def search_statuses(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_sync_db)):
    return master_service.search_statuses(db, q, limit)

@router.get("/priorities", response_model=List[MasterResponse])
def read_priorities(db: Session = Depends(get_sync_db)):
    return master_service.get_priorities(db)

@router.get("/priorities/search", response_model=List[MasterResponse])
def search_priorities(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_sync_db)):
    return master_service.search_priorities(db, q, limit)

@router.get("/roles", response_model=List[RoleResponse])
def read_roles(db: Session = Depends(get_sync_db)):
    from sqlalchemy import func, select
    from app.models.user import User
    from app.models.roles import Role as RoleModel

    user_count_sq = (
        select(User.role_id, func.count(User.id).label("cnt"))
        .where(User.role_id.isnot(None))
        .group_by(User.role_id)
        .subquery()
    )
    rows = db.execute(
        select(RoleModel, func.coalesce(user_count_sq.c.cnt, 0).label("users_count"))
        .outerjoin(user_count_sq, RoleModel.id == user_count_sq.c.role_id)
    ).all()

    seen = set()
    result = []
    for role, uc in rows:
        n = role.name.strip().lower()
        if n not in seen:
            seen.add(n)
            result.append({
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.permissions or {},
                "users_count": uc,
            })
    return result

@router.get("/roles/search", response_model=List[RoleResponse])
def search_roles(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_sync_db)):
    from sqlalchemy import func, select
    from app.models.user import User
    from app.models.roles import Role as RoleModel

    user_count_sq = (
        select(User.role_id, func.count(User.id).label("cnt"))
        .where(User.role_id.isnot(None))
        .group_by(User.role_id)
        .subquery()
    )
    rows = db.execute(
        select(RoleModel, func.coalesce(user_count_sq.c.cnt, 0).label("users_count"))
        .outerjoin(user_count_sq, RoleModel.id == user_count_sq.c.role_id)
        .where(RoleModel.name.ilike(f"%{q}%"))
        .limit(limit)
    ).all()

    seen = set()
    result = []
    for role, uc in rows:
        n = role.name.strip().lower()
        if n not in seen:
            seen.add(n)
            result.append({
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.permissions or {},
                "users_count": uc,
            })
    return result

@router.get("/roles/{role_id}", response_model=RoleWithUsersResponse)
def read_role(role_id: int, db: Session = Depends(get_sync_db)):
    db_role = master_service.get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.post("/roles", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_sync_db), current_user=Depends(allow_role_manage)):
    return master_service.create_role(db, role.model_dump())

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_sync_db), current_user=Depends(allow_role_manage)):
    return master_service.update_role(db, role_id, role.model_dump(exclude_unset=True))

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_sync_db), current_user=Depends(allow_role_manage)):
    success = master_service.delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}

@router.post("/roles/bulk-permissions")
def update_bulk_role_permissions(update_data: BulkRolePermissionsUpdate, db: Session = Depends(get_sync_db), current_user=Depends(allow_role_manage)):
    try:
        master_service.update_bulk_role_permissions(db, update_data.role_permissions)
        return {"message": "Permissions updated successfully for all roles"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/roles/{role_id}/users/{user_email}")
def assign_user_to_role(role_id: int, user_email: str, db: Session = Depends(get_sync_db)):
    from sqlalchemy import select
    from app.models.user import User
    from app.models.roles import Role
    
    db_role = (db.execute(select(Role).filter(Role.id == role_id))).scalar_one_or_none()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    user = (db.execute(select(User).filter(User.email == user_email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email '{user_email}' not found in system.")
        
    user.role_id = role_id
    db.commit()
    return {"message": "User assigned to role successfully"}

@router.delete("/roles/{role_id}/users/{user_email}")
def remove_user_from_role(role_id: int, user_email: str, db: Session = Depends(get_sync_db)):
    from sqlalchemy import select
    from app.models.user import User
    
    user = (db.execute(select(User).filter(User.email == user_email, User.role_id == role_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in this role.")
        
    user.role_id = None
    db.commit()
    return {"message": "User removed from role successfully"}

@router.post("/roles/{role_id}/users/bulk")
def bulk_assign_users_to_role(role_id: int, user_emails: List[str], db: Session = Depends(get_sync_db)):
    from sqlalchemy import select, update
    from app.models.user import User
    from app.models.roles import Role
    
    db_role = (db.execute(select(Role).filter(Role.id == role_id))).scalar_one_or_none()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    if user_emails:
        db.execute(update(User).filter(User.email.in_(user_emails)).values(role_id=role_id))
        db.commit()
    return {"message": f"Users assigned to role successfully"}

@router.get("/skills", response_model=List[SkillResponse])
def read_skills(db: Session = Depends(get_sync_db)):
    return master_service.get_skills(db)

@router.get("/skills/search", response_model=List[SkillResponse])
def search_skills(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_sync_db)):
    return master_service.search_skills(db, q, limit)
