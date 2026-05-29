from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import (
    Boolean, Column, Date, ForeignKey, Integer,
    Numeric, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import event, select

from app.core.database import Base, AuditMixin

class TimeLog(AuditMixin, Base):
    __tablename__ = "timelogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    log_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    task_id: Mapped[Optional[int]]    = mapped_column(ForeignKey("tasks.id"), nullable=True)
    issue_id: Mapped[Optional[int]]   = mapped_column(ForeignKey("issues.id"), nullable=True)
    timesheet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("timesheets.id"), nullable=True)

    date: Mapped[date] = mapped_column(Date, nullable=False)

    daily_log_hours: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    time_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    billing_type: Mapped[str] = mapped_column(String(50), default="Billable")
    approval_status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)

    general_log: Mapped[bool] = mapped_column(Boolean, default=False)

    is_processed: Mapped[bool]                      = mapped_column(Boolean, default=False)
    previous_approval_status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)


    user       = relationship("User", foreign_keys=[user_id], lazy="selectin")
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    
    approval_status_master = relationship("MasterLookup", foreign_keys=[approval_status_id], lazy="selectin")
    previous_approval_status_master = relationship("MasterLookup", foreign_keys=[previous_approval_status_id], lazy="selectin")

    @property
    def approval_status(self) -> Optional[dict]:
        if self.approval_status_master:
            return {
                "id": self.approval_status_master.id,
                "value": self.approval_status_master.value,
                "label": self.approval_status_master.label,
                "color": self.approval_status_master.color
            }
        return None

    project = relationship("Project", back_populates="timelogs", lazy="selectin")

    task    = relationship("Task", back_populates="timelogs", lazy="selectin")
    issue   = relationship("Issue", lazy="selectin")
    timesheet = relationship("Timesheet", back_populates="timelogs", lazy="selectin")







import sqlalchemy as sa
from sqlalchemy import event, func, update as sa_update


def _recalc_task_total(connection: sa.engine.Connection, task_id: int) -> None:
    
    from app.models.task import Task

    total_row = connection.execute(
        sa.select(func.coalesce(func.sum(TimeLog.daily_log_hours), 0))
        .where(TimeLog.task_id == task_id)
    ).scalar()

    connection.execute(
        sa_update(Task)
        .where(Task.id == task_id)
        .values(cached_timelog_total=float(total_row or 0))
    )


def _on_timelog_insert(mapper, connection, target: TimeLog) -> None:
    if target.task_id:
        _recalc_task_total(connection, target.task_id)


def _on_timelog_update(mapper, connection, target: TimeLog) -> None:
    if target.task_id:
        _recalc_task_total(connection, target.task_id)


def _on_timelog_delete(mapper, connection, target: TimeLog) -> None:
    if target.task_id:
        _recalc_task_total(connection, target.task_id)


event.listen(TimeLog, "after_insert", _on_timelog_insert)
event.listen(TimeLog, "after_update", _on_timelog_update)
event.listen(TimeLog, "after_delete", _on_timelog_delete)

