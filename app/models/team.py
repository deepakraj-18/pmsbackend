from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base, AuditMixin
from app.models.user import user_team_link

class Team(AuditMixin, Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    team_email = Column(String(255), unique=True, index=True, nullable=False)
    budget_allocation = Column(Numeric(12, 2), default=0.00)
    description = Column(String(500), nullable=True)
    team_type = Column(String(50), nullable=True)
    max_team_size = Column(Integer, nullable=True)
    primary_communication_channel = Column(String(100), nullable=True)
    channel_id = Column(String(100), nullable=True)

    lead_email = Column(String(255), ForeignKey("users.email"), nullable=True)

    lead = relationship("User", back_populates="managed_teams", foreign_keys=[lead_email])

    members = relationship("User", secondary=user_team_link, back_populates="teams")

    @property
    def members_count(self) -> int:
        return len(self.members)
