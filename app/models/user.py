from enum import Enum
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean,DateTime, Enum as SqlEnum, func
from sqlalchemy.orm import Mapped , mapped_column, relationship

from app.db.database import Base

class RoleClassify(Enum):
    USER = "User"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    full_name: Mapped[str] = mapped_column(VARCHAR(255), unique=False)
    role: Mapped[RoleClassify] = mapped_column(SqlEnum(RoleClassify), default=RoleClassify.USER)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    own_clubs = relationship("Club",back_populates="owner_club")
    memberships = relationship("ClubMember", back_populates="member")
    assigned_activities = relationship("ClubActivity", back_populates="assignee")