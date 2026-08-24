from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import list_users
from app.dependencies.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/users" , tags=["Users"])

@router.get("/me", response_model= UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("", response_model= list[UserResponse])
def read_users(
    search: str | None = Query(default=None, description="Tìm theo tên hoặc Email"),
    is_active: bool | None = Query(default=None, description="Lọc theo status"),
    db: Session = Depends(get_db),
    auto_check_admin: User = Depends(get_current_admin_user),
):
    return list_users(db, search=search, is_active=is_active)