from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User, RoleClassify
from app.utils.exceptions import ForbiddenException, UnauthorizedException, NotFoundException

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    print("Token sau khi xu ly:", token)

    if token is None:
        raise UnauthorizedException("Access Token Is Missing ...")

    token = token.credentials

    payload = decode_access_token(token)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException("Token Invalid Or Expired")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Token Invalid")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise NotFoundException("User Not Found")

    if not user.is_active:
        raise ForbiddenException("This Account Has Been Disabled")

    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleClassify.ADMIN:
        raise ForbiddenException("Only Admin Can Access This!!")
    return current_user