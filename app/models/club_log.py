from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, TEXT, VARCHAR, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ClubLog(Base):
    __tablename__ = "club_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    club_id: Mapped[int | None] = mapped_column(ForeignKey("clubs.id", ondelete="SET NULL"),nullable=True,)

    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False,)

    action: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    details: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)