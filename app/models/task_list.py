from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base, AuditMixin

class TaskList(AuditMixin, Base):
    __tablename__ = "task_lists"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)

    project = relationship("Project", back_populates="task_lists")
    milestone = relationship("Milestone", back_populates="task_lists")
    tasks = relationship("Task", back_populates="task_list", cascade="all, delete-orphan")
