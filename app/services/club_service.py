from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.club import Club, ClubMember, ClubMemberRole
from app.schemas.club import ClubCreate
from app.utils.exceptions import BadRequestException, NotFoundException, ForbiddenException

def create_club(db: Session, club_data: ClubCreate):
    existing_club = db.query(Club).filter(func.lower(Club.name) == club_data.name.lower()).first()
    if existing_club:
        raise BadRequestException("Câu lạc bộ này đã tồn tại")

    new_club = Club(
        name= club_data.name,
        description = club_data.description,
        owner_id = club_data.owner_id
    )

    try:
        db.add(new_club)
        db.flush()

        owner_membership = ClubMember(
            club_id= new_club.id, user_id= new_club.owner_id , role= ClubMemberRole.OWNER
        )

        db.add(owner_membership)
        db.flush()

    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(new_club)

    return new_club


def list_user_clubs(db: Session, user_id: int, search: str = None):

    print(search)
    print(user_id)

    query = (db.query(Club)
             .join(ClubMember, ClubMember.club_id == Club.id)
             .filter(ClubMember.user_id == user_id)
             )

    print(query)

    if search:
        query = query.filter(Club.name.ilike(f"%{search}%"))

    return query.order_by(Club.id).all()


def get_club(db: Session, club_id: int):
    club = db.query(Club).filter(Club.id == club_id).first()
    if club is None:
        raise NotFoundException("Clb không tồn tại!")
    return club


def require_member(db: Session, club_id: int, user_id: int) -> ClubMember:
    membership = db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id).first()
    if membership is None:
        raise ForbiddenException("Bạn không có tham gia clb này!")
    return membership

def require_owner(db: Session, club_id: int, user_id: int) -> ClubMember:
    membership = require_member(db, club_id, user_id)
    if membership.role != ClubMemberRole.OWNER:
        raise ForbiddenException("Chỉ Owner mới có thể tiếp tục")
    return membership

def add_member(db: Session, club_id: int, target_user_id: int) -> ClubMember:
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if target_user is None:
        raise NotFoundException("Người dùng không tồn tại")

    existing = db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == target_user_id).first()


    if existing is not None:
        raise BadRequestException("Người dùng đã có trong Clb")

    member = ClubMember(club_id=club_id, user_id=target_user_id, role=ClubMemberRole.MEMBER)

    try:
        db.add(member)
        db.flush()
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(member)

    return member