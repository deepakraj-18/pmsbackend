from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Boolean, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.config import settings
from app.core.database import Base, AuditMixin, utcnow

user_team_link = Table(
    "user_team_link",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("team_id", Integer, ForeignKey("teams.id"), nullable=False),
    Column("created_at", DateTime(timezone=False), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), server_default=utcnow(), nullable=False),
    Column("updated_at", DateTime(timezone=False), default=None, onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
)

user_skill_link = Table(
    "user_skill_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
    Column("created_at", DateTime(timezone=False), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), server_default=utcnow(), nullable=False),
    Column("updated_at", DateTime(timezone=False), default=None, onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False)
)

class User(AuditMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint('email', name='uq_user_email'),)

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    job_title = Column(String(100), nullable=True)
    join_date = Column(Date, default=lambda: datetime.now(timezone.utc).date(), nullable=True)

    password_hash = Column(String(255), nullable=True)

    display_name = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    language = Column(String(50), default=settings.DEFAULT_LANGUAGE, nullable=True)
    timezone = Column(String(100), default=None, nullable=True)

    o365_id = Column(String(255), unique=True, index=True, nullable=True)
    is_synced = Column(Boolean, default=False)
    is_external = Column(Boolean, default=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("user_statuses.id"), nullable=True)

    manager_email = Column(String(255), ForeignKey("users.email"), nullable=True)

    role = relationship("Role", lazy="joined")
    status = relationship("UserStatus", lazy="joined")
    manager = relationship("User", remote_side=[email], lazy="select")

    teams = relationship("Team", secondary=user_team_link, back_populates="members")
    skills = relationship("Skill", secondary=user_skill_link, backref="users")
    projects = relationship("Project", secondary="project_members", viewonly=True)

    managed_teams = relationship("Team", back_populates="lead", foreign_keys="Team.lead_email")

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
