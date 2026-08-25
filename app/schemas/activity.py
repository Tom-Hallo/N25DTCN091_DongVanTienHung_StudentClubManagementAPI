from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.activity import ActivityPriority, ActivityStatus


class ClubActivityBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: ActivityPriority = ActivityPriority.MEDIUM

class ClubActivityCreateForm(ClubActivityBase):
    assignee_id: int | None = None


class ClubActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: ActivityPriority | None = None
    status: ActivityStatus | None = None
    assignee_id: int | None = None


class ClubActivityResponse(ClubActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    assignee_id: int | None
    status: ActivityStatus
    created_at: datetime