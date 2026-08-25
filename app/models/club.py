from enum import Enum
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, DateTime, ForeignKey, func, Enum as SqlEnum
from sqlalchemy.orm import Mapped , mapped_column, relationship

from app.db.database import Base

class ClubMemberRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(255), unique=False)
    description: Mapped[str] = mapped_column(VARCHAR(255), unique=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner_club = relationship("User", back_populates="own_clubs")
    members = relationship("ClubMember", back_populates="club")
    activities = relationship("ClubActivity", back_populates="club")
    

class ClubMember(Base):
    __tablename__ = "club_members"

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    role: Mapped[ClubMemberRole] = mapped_column(SqlEnum(ClubMemberRole), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    member = relationship("User",back_populates="memberships")
    club = relationship("Club", back_populates="members")