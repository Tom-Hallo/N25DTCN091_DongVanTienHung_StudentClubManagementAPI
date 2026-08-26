from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


from app.models.activity import ActivityPriority, ActivityStatus


class ClubActivityBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: ActivityPriority = ActivityPriority.MEDIUM

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
        
    #Check thời gian due_date có phải là tương lai không
    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, value):
        if value is None:
            return value
        now = datetime.now(timezone.utc)
        compare_value = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        if compare_value < now:
            raise ValueError("due_date không được nằm trong quá khứ")
        return value

class ClubActivityCreateForm(ClubActivityBase):
    assignee_id: int | None = None


class ClubActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: ActivityPriority | None = None
    status: ActivityStatus | None = None
    assignee_id: int | None = None

    @field_validator("assignee_id", mode="before")
    @classmethod
    def empty_assignee_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ClubActivityResponse(ClubActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    assignee_id: int | None
    status: ActivityStatus
    created_at: datetime


class ActivityCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class ActivityCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    user_id: int
    content: str
    created_at: datetime


class ActivityAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    user_id: int
    original_name: str
    content_type: str
    file_size: int
    file_path: str
    created_at: datetime