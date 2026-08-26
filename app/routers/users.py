from fastapi import APIRouter, Query, Depends, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.response import api_response
from app.services.user_service import list_users
from app.dependencies.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/users" , tags=["Users"])

@router.get("/me", response_model= UserResponse,
            summary="Xem thông tin người dùng",
            description="Xem thông tin của chính mình.")
def read_current_user(request: Request, current_user: User = Depends(get_current_user)):

    show_current_user = UserResponse.model_validate(current_user).model_dump(mode="json")

    # return current_user

    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=api_response(
                status_code=status.HTTP_200_OK,
                message="Đã Lấy thông tin cá nhân thành công",
                data=show_current_user,
                path=request.url.path,
            ),
        )

@router.get("", response_model= list[UserResponse],
            summary="Xem thông tin toàn bộ người dùng (Admin)",
            description="Chỉ có admin có quyền xem thông tin người dùng.")
def read_users(
    request: Request,
    search: str | None = Query(default=None, description="Tìm theo tên hoặc Email"),
    is_active: bool | None = Query(default=None, description="Lọc theo status"),
    db: Session = Depends(get_db),
    auto_check_admin: User = Depends(get_current_admin_user),
):

    list = list_users(db, search=search, is_active=is_active)

    list_users_response = [
        UserResponse.model_validate(club).model_dump(mode="json")
        for club in list
    ]

    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=api_response(
                status_code=status.HTTP_200_OK,
                message="Đã Lấy thông tin người dùng thành công",
                data=list_users_response,
                path=request.url.path,
            ),
        )