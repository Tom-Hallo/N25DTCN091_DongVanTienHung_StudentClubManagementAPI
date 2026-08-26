from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.club import ClubCreate
from app.models.club import Club, ClubMember, ClubMemberRole
from app.models.activity import ClubActivity
from app.models.club_log import ClubLog
from app.utils.exceptions import BadRequestException, NotFoundException, ForbiddenException, HTTPConflict

def create_club(db: Session, club_data: ClubCreate, actor_id: int):
    existing_club = db.query(Club).filter(
        func.lower(Club.name) == club_data.name.lower(),
        Club.is_deleted.is_(False),
        Club.deleted_at.is_(None),
    ).first()
    if existing_club:
        raise HTTPConflict("Câu lạc bộ này đã tồn tại") 

    new_club = Club(
        name= club_data.name,
        description = club_data.description,
        owner_id = club_data.owner_id
    )

    try:
        db.add(new_club)
        db.flush()

        owner_membership = ClubMember(club_id= new_club.id, user_id= new_club.owner_id , role= ClubMemberRole.OWNER)

        db.add(owner_membership)
        db.flush()
        db.add(ClubLog(
            club_id=new_club.id,
            actor_id=actor_id,
            action="CREATE_CLUB",
            details="Tạo câu lạc bộ",
        ))

    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(new_club)

    return new_club

def list_user_clubs(db: Session, user_id: int, search: str = None):

    query = (db.query(Club)
             .join(ClubMember, ClubMember.club_id == Club.id)
             .filter(
                 ClubMember.user_id == user_id,
                 Club.is_deleted.is_(False),
                 Club.deleted_at.is_(None),
             )
             )

    if search:
        query = query.filter(Club.name.ilike(f"%{search}%"))

    return query.order_by(Club.id).all()

def get_club(db: Session, club_id: int):
    club = db.query(Club).filter(
        Club.id == club_id,
        Club.is_deleted.is_(False),
        Club.deleted_at.is_(None),
    ).first()
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

def add_member(db: Session, club_id: int, target_user_id: int, actor_id: int) -> ClubMember:
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if target_user is None:
        raise NotFoundException("Người dùng không tồn tại")

    existing = db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == target_user_id).first()


    if existing is not None:
        raise HTTPConflict("Người dùng đã có trong Clb")

    member = ClubMember(club_id=club_id, user_id=target_user_id, role=ClubMemberRole.MEMBER)

    try:
        db.add(member)
        db.flush()
        db.add(ClubLog(
            club_id=club_id,
            actor_id=actor_id,
            action="ADD_MEMBER",
            details=f"Thêm user_id={target_user_id}",
        ))
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(member)

    return member

def update_club(db: Session, club: Club, name: str, description: str, actor_id: int) -> Club:
    changes = []
    if name:
        club.name = name
        changes.append("name")
    if description:
        club.description = description
        changes.append("description")

    try:
        db.add(club)
        db.flush()
        if changes:
            db.add(ClubLog(
                club_id=club.id,
                actor_id=actor_id,
                action="UPDATE_CLUB",
                details=f"Cập nhật: {', '.join(changes)}",
            ))
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(club)

    return club

def delete_club(db: Session, club: Club, actor_id: int) -> None:
    try:
        db.add(ClubLog(
            club_id=club.id,
            actor_id=actor_id,
            action="DELETE_CLUB",
            details=f"Xóa mềm câu lạc bộ: {club.name}",
        ))
        club.is_deleted = True
        club.deleted_at = func.now()
        db.commit()

    except Exception:
        db.rollback()
        raise

def remove_member(db: Session, club_id: int, target_user_id: int, actor_id: int) -> None:
    membership = db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == target_user_id).first()
    if membership is None:
        raise NotFoundException("Người dùng không phải thành viên của clb")

    if membership.role == ClubMemberRole.OWNER:
        owner_count = (
            db.query(ClubMember)
            .filter(ClubMember.club_id == club_id, ClubMember.role == ClubMemberRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise BadRequestException("Không thể xóa owner cuối cùng của clb")

    try:
        db.delete(membership)
        db.add(ClubLog(
            club_id=club_id,
            actor_id=actor_id,
            action="REMOVE_MEMBER",
            details=f"Xóa user_id={target_user_id}",
        ))
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()

def list_members(db: Session, club_id: int) -> list[dict]:
    rows = (
        db.query(ClubMember, User)
        .join(User, User.id == ClubMember.user_id)
        .filter(ClubMember.club_id == club_id)
        .order_by(ClubMember.role, User.full_name)
        .all()
    )

    return [
        {
            "user_id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": member.role,
            "joined_at": member.joined_at,
        }
        for member, user in rows
    ]


def list_logs(db: Session, club_id: int) -> list[ClubLog]:
    return (
        db.query(ClubLog)
        .filter(ClubLog.club_id == club_id)
        .order_by(ClubLog.created_at.desc(), ClubLog.id.desc())
        .all()
    )
