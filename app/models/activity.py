from enum import Enum
from datetime import datetime
from sqlalchemy import VARCHAR, DateTime, ForeignKey, func, Enum as SqlEnum, TEXT
from sqlalchemy.orm import Mapped , mapped_column, relationship

from app.db.database import Base

class ActivityStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class ActivityPriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ClubActivity(Base):
    __tablename__ = "club_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=False)
    
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[ActivityStatus] = mapped_column(SqlEnum(ActivityStatus), nullable=False)
    priority: Mapped[ActivityPriority] = mapped_column(SqlEnum(ActivityPriority), nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    club = relationship("Club", back_populates="activities")
    assignee = relationship("User", back_populates="assigned_activities")