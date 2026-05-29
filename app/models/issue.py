from __future__ import annotations

from enum import Enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum, ForeignKey,
    Integer, Numeric, String, Text, Table
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, AuditMixin

issue_followers = Table(
    "issue_followers",
    Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

issue_assignees = Table(
    "issue_assignees",
    Base.metadata,
    Column("issue_id", Integer, ForeignKey("issues.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class Issue(AuditMixin, Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    bug_name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("milestones.id"), nullable=True)
    associated_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)

    reporter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    status_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)
    priority_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)
    severity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)
    classification_id: Mapped[Optional[int]] = mapped_column(ForeignKey("master_lookups.id"), nullable=True)



    
    module: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[Optional[str]]   = mapped_column(String(500), nullable=True)
    flag: Mapped[Optional[str]]   = mapped_column(String(50), nullable=True)  

    reproducible_flag: Mapped[bool] = mapped_column(Boolean, default=True)

    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]]   = mapped_column(Date, nullable=True)

    last_closed_time: Mapped[Optional[datetime]]   = mapped_column(DateTime, nullable=True)
    last_modified_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    estimated_hours: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    previous_status_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("master_lookups.id"), nullable=True
    )



    project  = relationship("Project", back_populates="issues", lazy="selectin")
    milestone = relationship("Milestone", foreign_keys=[milestone_id], lazy="selectin")
    
    status_master   = relationship("MasterLookup", foreign_keys=[status_id], lazy="selectin")
    priority_master = relationship("MasterLookup", foreign_keys=[priority_id], lazy="selectin")
    severity_master = relationship("MasterLookup", foreign_keys=[severity_id], lazy="selectin")
    classification_master = relationship("MasterLookup", foreign_keys=[classification_id], lazy="selectin")
    reporter = relationship("User", foreign_keys=[reporter_id], lazy="selectin")

    assignee = relationship("User", foreign_keys=[assignee_id], lazy="selectin")

    followers = relationship("User", secondary=issue_followers, lazy="selectin")
    assignees = relationship("User", secondary=issue_assignees, lazy="selectin")

    documents = relationship("Document", secondary="issue_document_link", back_populates="issues", lazy="selectin")

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
    def severity(self) -> Optional[dict]:


        if self.severity_master:
            return {
                "id": self.severity_master.id,
                "label": self.severity_master.label,
                "value": self.severity_master.value,
                "color": self.severity_master.color,
                "category": self.severity_master.category
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

    @property
    def classification(self) -> Optional[dict]:



        if self.classification_master:
            return {
                "id": self.classification_master.id,
                "label": self.classification_master.label,
                "value": self.classification_master.value,
                "color": self.classification_master.color,
                "category": self.classification_master.category
            }
        return None
