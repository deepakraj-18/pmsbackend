from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, AuditMixin


class ProjectPhase(AuditMixin, Base):
    __tablename__ = "project_phases"

    id         = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    phase      = Column(String(64), nullable=False)
    status     = Column(String(32), nullable=False, default="active")

    project = relationship("Project", foreign_keys=[project_id])


class AgentRun(AuditMixin, Base):
    __tablename__ = "agent_runs"

    id              = Column(Integer, primary_key=True, index=True)
    project_id      = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_id        = Column(Integer, ForeignKey("project_phases.id", ondelete="SET NULL"), nullable=True)
    agent_type      = Column(String(64), nullable=False)
    model_used      = Column(String(128), nullable=True)
    status          = Column(String(32), nullable=False, default="running")
    output_doc_path = Column(String(512), nullable=True)
    tokens_used     = Column(Integer, nullable=True)
    error_message   = Column(Text, nullable=True)
    completed_at    = Column(DateTime, nullable=True)

    project = relationship("Project", foreign_keys=[project_id])
    phase   = relationship("ProjectPhase", foreign_keys=[phase_id])


class TestCase(AuditMixin, Base):
    __tablename__ = "test_cases"

    id               = Column(Integer, primary_key=True, index=True)
    project_id       = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id          = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    title            = Column(String(256), nullable=False)
    description      = Column(Text, nullable=True)
    steps            = Column(Text, nullable=True)
    expected_result  = Column(Text, nullable=True)
    type             = Column(String(32), nullable=True, default="e2e")
    environment      = Column(String(32), nullable=True)
    priority         = Column(String(32), nullable=True, default="Medium")
    created_by_agent = Column(String(64), nullable=True)

    project = relationship("Project", foreign_keys=[project_id])


class TestReport(AuditMixin, Base):
    __tablename__ = "test_reports"

    id                = Column(Integer, primary_key=True, index=True)
    project_id        = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id      = Column(Integer, ForeignKey("test_cases.id", ondelete="SET NULL"), nullable=True)
    environment       = Column(String(32), nullable=True)
    result            = Column(String(32), nullable=False, default="pending")
    notes             = Column(Text, nullable=True)
    executed_by_agent = Column(String(64), nullable=True)

    project   = relationship("Project", foreign_keys=[project_id])
    test_case = relationship("TestCase", foreign_keys=[test_case_id])
