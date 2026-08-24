from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.club import ClubMemberRole


class ClubBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class ClubCreate(ClubBase):
    owner_id: int


class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    owner_id: int | None = None


class ClubResponse(ClubBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime


class ClubMemberBase(BaseModel):
    user_id: int
    club_id: int
    role: ClubMemberRole = ClubMemberRole.MEMBER


class ClubMemberCreate(ClubMemberBase):
    pass


class ClubMemberUpdate(BaseModel):
    role: ClubMemberRole | None = None


class ClubMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    club_id: int
    user_id: int
    role: ClubMemberRole
    joined_at: datetime