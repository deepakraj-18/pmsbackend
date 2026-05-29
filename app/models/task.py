from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, Date, ForeignKey, Integer,
    Numeric, String, Table, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, object_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

from app.core.database import Base, AuditMixin

task_owners = Table(
    "task_owners",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

task_assignees = Table(
    "task_assignees",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

class Task(AuditMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    task_name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project_id: Mapped[Optional[int]]    = mapped_column(ForeignKey("projects.id"), nullable=True)
    task_list_id: Mapped[Optional[int]]  = mapped_column(ForeignKey("task_lists.id"), nullable=True)
    milestone_id: Mapped[Optional[int]]  = mapped_column(ForeignKey("milestones.id"), nullable=True)
    associated_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)

    assignee_id: Mapped[Optional[int]]   = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    owner_id: Mapped[Optional[int]]      = mapped_column(ForeignKey("users.id"), nullable=True)

    status_id: Mapped[Optional[int]]   = mapped_column(ForeignKey("master_lookups.id"), nullable=True)
    priority_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)
    tags: Mapped[Optional[str]]     = mapped_column(String(500), nullable=True)

    start_date: Mapped[Optional[date]]      = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]]        = mapped_column(Date, nullable=True)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    _duration: Mapped[Optional[int]] = mapped_column("duration", Integer, nullable=True)
    completion_percentage: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)



    estimated_hours: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    work_hours: Mapped[Optional[float]]      = mapped_column(Numeric(10, 2), default=0, nullable=True)
    cached_timelog_total: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0, nullable=True)
    billing_type: Mapped[str]                = mapped_column(String(50), default="Billable")

    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    previous_status_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("master_lookups.id"), nullable=True
    )



    project   = relationship("Project", back_populates="tasks", lazy="selectin")
    task_list = relationship("TaskList", back_populates="tasks", lazy="selectin")
    milestone = relationship("Milestone", foreign_keys=[milestone_id], lazy="selectin")
    
    status_master = relationship("MasterLookup", foreign_keys=[status_id], lazy="selectin")
    priority_master = relationship("MasterLookup", foreign_keys=[priority_id], lazy="selectin")

    assignee     = relationship("User", foreign_keys=[assignee_id], lazy="selectin")
    creator      = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    single_owner = relationship("User", foreign_keys=[owner_id], lazy="selectin")

    owners    = relationship("User", secondary=task_owners, lazy="selectin")
    assignees = relationship("User", secondary=task_assignees, lazy="selectin")

    associated_team = relationship("Team", foreign_keys=[associated_team_id], lazy="selectin")

    timelogs: Mapped[List["TimeLog"]] = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan", lazy="selectin")

    @property
    def timelog_total(self) -> float:
        from sqlalchemy.orm.attributes import instance_state
        if 'timelogs' in instance_state(self).unloaded:
            return 0.0
        if not self.timelogs:
            return 0.0
        return sum(float(log.daily_log_hours or 0) for log in self.timelogs)

    @hybrid_property
    def difference(self) -> float:
        plan_hours = float(self.work_hours or self.estimated_hours or 0)
        t_total = float(self.cached_timelog_total or 0)
        return round(plan_hours - t_total, 2)
        
    @difference.expression
    def difference(cls):
        return func.coalesce(cls.work_hours, cls.estimated_hours, 0) - func.coalesce(cls.cached_timelog_total, 0)

    @property
    def status(self) -> Optional[dict]:


        if self.status_master:
            return {
                "id": self.status_master.id,
                "label": self.status_master.label,
                "value": self.status_master.value,
                "color": self.status_master.color,
                "category": self.status_master.category
            }
        return None

    @property
    def priority(self) -> Optional[dict]:


        if self.priority_master:
            return {
                "id": self.priority_master.id,
                "label": self.priority_master.label,
                "value": self.priority_master.value,
                "color": self.priority_master.color,
                "category": self.priority_master.category
            }
        return None

    @hybrid_property
    def duration(self) -> Optional[int]:
        if self._duration is not None:
            return self._duration
        if self.due_date and self.start_date:
            return (self.due_date - self.start_date).days
        return None

    @duration.setter
    def duration(self, value: Optional[int]):
        self._duration = value
