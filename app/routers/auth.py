from fastapi import APIRouter, Form, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import auth_service
from app.schemas.user import UserCreate, UserResponse
from app.utils.rate_limiter import check_rate_limit
from app.utils.response import api_response

router = APIRouter(prefix="/auth" , tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED,
            summary="Đăng kí tài khoản",
            description="Tạo một tài khoản để sử dụng các chức năng.")
def auth_register(
    request: Request,
    user_data: UserCreate = Form(...),
    db: Session = Depends(get_db)
 ):
    new_user = auth_service.create_user(db=db, user_data=user_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=api_response(
            status_code=status.HTTP_201_CREATED,
            message="Đăng ký tài khoản thành công",
            data=UserResponse.model_validate(new_user).model_dump(mode="json"),
            path=request.url.path,
        ),
    )


@router.post("/login",
            status_code=status.HTTP_200_OK,
            summary="Đăng nhập tài khoản",
            description="Đằng nhập để lấy access token và refresh token")
def auth_login(
    request: Request,
    email: str = Form(..., description="Nhập Email người dùng"),
    password: str = Form(..., description="Nhập mật khẩu người dùng"),
    db: Session = Depends(get_db)
):

    """
    Giới hạn số lần đăng nhập
    """
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"{client_ip}:{email}")

    user_authentiacted = auth_service.authenticate_user(db=db, email= email, password= password)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Đăng nhập thành công",
            data=auth_service.issue_tokens(user_authentiacted),
            path=request.url.path,
        ),
    )


@router.post("/refresh",
            status_code=status.HTTP_200_OK,
            summary="Refresh token",
            description="Nhập refresh token để tạo lại cái mới.")
def auth_refresh(
    request: Request,
    refresh_token: str = Form(..., description="Nhập refresh token"),
    db: Session = Depends(get_db),
):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Làm mới token thành công",
            data=auth_service.refresh_access_token(db, refresh_token),
            path=request.url.path,
        ),
    )