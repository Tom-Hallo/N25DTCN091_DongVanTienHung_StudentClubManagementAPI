from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.exceptions import BadRequestException, UnauthorizedException, ForbiddenException ,HTTPConflict
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token

def create_user(db: Session, user_data: UserCreate):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPConflict("Email đã tồn tại")

    hashed_pwd = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        password_hash=hashed_pwd,
        full_name=user_data.full_name,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Logic Đăng nhập:
    1. Tìm người dùng trong database theo email.
    2. Nếu không tìm thấy, hoặc nếu có mà mật khẩu không khớp -> lỗi 400.
    3. Trả về thông tin người dùng nếu thành công.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise BadRequestException("Email hoặc mật khẩu không chính xác")

    return user

def issue_tokens(user: User) -> dict:
    payload = {"sub": str(user.id), "role": user.role.value}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
    }

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    payload = decode_access_token(refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise UnauthorizedException("Refresh token không hợp lệ hoặc đã hết hạn")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first() if user_id else None

    if user is None:
        raise UnauthorizedException("Người dùng không tồn tại")

    if not user.is_active:
        raise ForbiddenException("Tài khoản đã bị vô hiệu hóa")

    new_payload = {"sub": str(user.id), "role": user.role.value}
    return {
        "access_token": create_access_token(new_payload),
        "token_type": "bearer",
    }