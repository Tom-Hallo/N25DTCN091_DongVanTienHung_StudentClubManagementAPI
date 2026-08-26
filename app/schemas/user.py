from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import RoleClassify


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_full_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)
    # role: RoleClassify = RoleClassify.USER


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=6, max_length=100)
    role: RoleClassify | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: RoleClassify
    is_active: bool
    created_at: datetime