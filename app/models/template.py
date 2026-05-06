from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, AuditMixin


class ProjectTemplate(AuditMixin, Base):
    __tablename__ = "project_templates"

    id           = Column(Integer, primary_key=True, index=True)
    public_id    = Column(String(50), unique=True, index=True, nullable=True)
    name         = Column(String(255), nullable=False, index=True, unique=True)
    description  = Column(Text, nullable=True)
    billing_type = Column(String(50), nullable=True)
    is_public    = Column(Boolean, default=True, nullable=False)

    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    tasks = relationship(
        "TemplateTask",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateTask.order_index",
        lazy="selectin",
    )


class TemplateTask(Base):
    __tablename__ = "template_tasks"

    id              = Column(Integer, primary_key=True, index=True)
    template_id     = Column(
        Integer,
        ForeignKey("project_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title           = Column(String(255), nullable=False)
    description     = Column(Text, nullable=True)
    estimated_hours = Column(Numeric(10, 2), nullable=True)
    duration        = Column(Integer, nullable=True)
    billing_type    = Column(String(50), nullable=True)
    tags            = Column(String(500), nullable=True)
    order_index     = Column(Integer, default=0, nullable=False)

    template = relationship("ProjectTemplate", back_populates="tasks")
