from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_sync_db
from app.core.security import get_current_user, allow_authenticated, allow_pm, is_employee_only, allow_role_manage
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserListResponse
from app.services import user_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/search", response_model=List[UserResponse])
def search_users(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_sync_db),
):
    return user_service.search_users(db, query=q, limit=limit)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_role_manage),
):
    if user_service.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.username and user_service.get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_service.create_user(db=db, user=user, actor_id=current_user.o365_id or str(current_user.id))

@router.get("/", response_model=UserListResponse)
def read_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role_id: Optional[List[int]] = Query(None),
    db: Session = Depends(get_sync_db),
):
    return user_service.get_users(db, skip=skip, limit=limit, search=search, role_ids=role_id)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_sync_db),
):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    if is_employee_only(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only update your own profile.")
    db_user = user_service.update_user(
        db, user_id=user_id, user_update=user_update, actor_id=current_user.o365_id or str(current_user.id)
    )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_role_manage),
):
    success = user_service.delete_user(db, user_id=user_id, actor_id=current_user.o365_id or str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
