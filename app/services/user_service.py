from sqlalchemy.orm import Session

from app.models.user import User

def list_users(db: Session, search: str | None = None, is_active: bool | None = None,) -> list:
    query = db.query(User)

    if search:
        pattern = f"%{search}%"
        query = query.filter((User.full_name.ilike(pattern)) | (User.email.ilike(pattern)))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.order_by(User.id).all()