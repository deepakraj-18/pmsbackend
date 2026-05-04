from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_sync_db
from app.core.security import allow_authenticated, allow_team_lead_plus
from app.core.dependencies import auto_populate_milestone
from app.schemas.milestone import MilestoneCreate, MilestoneResponse, MilestoneUpdate
from app.services import milestone_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])

@router.post("/", response_model=MilestoneResponse)
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):

    auto_populate_milestone(milestone, current_user)
    return milestone_service.create_milestone(
        db=db,
        milestone=milestone,
        actor_id=current_user.o365_id or str(current_user.id),
    )

@router.get("/", response_model=List[MilestoneResponse])
def read_milestones(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_sync_db),
):
    return milestone_service.get_milestones(
        db,
        skip=skip,
        limit=limit,
        project_id=project_id,
    )

@router.get("/search", response_model=List[MilestoneResponse])
def search_milestones(
    q: str = Query(..., min_length=1),
    project_id: Optional[int] = None,
    limit: int = Query(50, gt=0, le=100),
    db: Session = Depends(get_sync_db),
):
    from app.models.milestone import Milestone
    from app.services.milestone_service import _batch_enrich_milestones
    stmt = (
        db.query(Milestone)
        .filter(Milestone.milestone_name.ilike(f"%{q}%"))
    )
    if project_id:
        stmt = stmt.filter(Milestone.project_id == project_id)
    milestones = stmt.limit(limit).all()
    _batch_enrich_milestones(db, milestones)
    return milestones


@router.get("/{milestone_id}", response_model=MilestoneResponse)
def read_milestone(
    milestone_id: int,
    db: Session = Depends(get_sync_db),
):
    db_milestone = milestone_service.get_milestone(db, milestone_id=milestone_id)
    if db_milestone is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return db_milestone

@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    updated = milestone_service.update_milestone(
        db,
        milestone_id,
        milestone_in,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return updated

@router.delete("/{milestone_id}", status_code=204)
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_team_lead_plus),
):
    success = milestone_service.delete_milestone(
        db,
        milestone_id=milestone_id,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Milestone not found")
