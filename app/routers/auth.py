from fastapi import APIRouter, Form, Depends, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import auth_service
from app.schemas.user import UserCreate, UserResponse
from app.utils.rate_limiter import check_rate_limit

router = APIRouter(prefix="/auth" , tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def auth_register(
    user_data: UserCreate = Form(...),
    db: Session = Depends(get_db)
 ):
    new_user = auth_service.create_user(db=db, user_data=user_data)
    return new_user


@router.post("/login")
def auth_login(
    request: Request,
    email: str = Form(..., description="Nhập Email người dùng"),
    password: str = Form(..., description="Nhập mật khẩu người dùng"),
    db: Session = Depends(get_db)
):

    """
    Giới hạn số lần đăng nhập
    """
    # client_ip = request.client.host if request.client else "unknown"
    # check_rate_limit(f"{client_ip}:{email}")

    user_authentiacted = auth_service.authenticate_user(db=db, email= email, password= password)

    return auth_service.issue_tokens(user_authentiacted)


@router.post("/refresh")
def auth_refresh( refresh_token: str = Form(..., description="Nhập refresh token"), db: Session = Depends(get_db),
):
    return auth_service.refresh_access_token(db, refresh_token)