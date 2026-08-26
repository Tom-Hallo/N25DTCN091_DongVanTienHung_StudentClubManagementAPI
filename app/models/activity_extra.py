from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, TEXT, VARCHAR, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ActivityComment(Base):
    __tablename__ = "activity_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("club_activities.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ActivityAttachment(Base):
    __tablename__ = "activity_attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("club_activities.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    original_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
