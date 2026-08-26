from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.club import Club, ClubMember, ClubMemberRole
from app.models.activity import ClubActivity, ActivityStatus, ActivityPriority
from app.models.club_log import ClubLog
from app.models.activity_extra import ActivityAttachment, ActivityComment
from app.schemas.activity import ClubActivityCreateForm, ClubActivityUpdate
from app.utils.exceptions import BadRequestException, NotFoundException, ForbiddenException, HTTPConflict
from app.services.club_service import require_member, require_owner


ALLOWED_SORT_FIELDS = {
    "created_at": ClubActivity.created_at,
    "due_date": ClubActivity.due_date,
}

MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024
ALLOWED_ATTACHMENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}
ATTACHMENT_DIRECTORY = Path("uploads") / "activities"


def validate_assignee(db: Session, club_id: int, assignee_id: int) -> None:
    """Assignee bắt buộc phải là thành viên đang sinh hoạt trong club đó."""
    membership = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == assignee_id)
        .first()
    )
    if membership is None:
        raise BadRequestException("Người được gán không phải là thành viên của câu lạc bộ")

# region ================================ Tạo hoạt đông CLB (Mem/Own) ================================
def create_activity(db: Session, club_id: int, data: ClubActivityCreateForm, actor: User) -> ClubActivity:
    # Bất kỳ thành viên nào (Member/Owner) cũng có quyền tạo
    require_member(db, club_id, actor.id)

    if data.assignee_id is not None:
            validate_assignee(db, club_id, data.assignee_id)

    existing_activity_query = db.query(ClubActivity).filter(
        ClubActivity.club_id == club_id,
        func.lower(ClubActivity.title) == data.title.strip().lower(),
    )

    if data.due_date is None:
        existing_activity_query = existing_activity_query.filter(
            ClubActivity.due_date.is_(None)
        )
    else:
        existing_activity_query = existing_activity_query.filter(
            extract("year", ClubActivity.due_date) == data.due_date.year,
            extract("month", ClubActivity.due_date) == data.due_date.month,
            extract("day", ClubActivity.due_date) == data.due_date.day,
            extract("hour", ClubActivity.due_date) == data.due_date.hour,
            extract("minute", ClubActivity.due_date) == data.due_date.minute,
        )

    if existing_activity_query.first() is not None:
        raise HTTPConflict("Hoạt động có cùng tên và thời gian đã tồn tại trong CLB")

    new_activity = ClubActivity(
        club_id=club_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        priority=data.priority,
        assignee_id=data.assignee_id,
        status=ActivityStatus.TODO,
    )

    try:
        db.add(new_activity)
        db.flush()
        db.add(ClubLog(
            club_id=club_id,
            actor_id=actor.id,
            action="CREATE_ACTIVITY",
            details=f"Tạo hoạt động: {new_activity.title}",
        ))
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(new_activity)

    return new_activity
#endregion

# region ================================ Xem các hoạt đông của CLB đó ================================
def list_activities(
    db: Session,
    club_id: int,
    actor: User,
    status: ActivityStatus | None = None,
    priority: ActivityPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    size: int = 10,
) -> tuple[list[ClubActivity], int]:
    # Phải là thành viên club mới được xem -> không lộ hoạt động của club khác
    require_member(db, club_id, actor.id)

    query = db.query(ClubActivity).filter(ClubActivity.club_id == club_id)

    if status is not None:
        query = query.filter(ClubActivity.status == status)
    if priority is not None:
        query = query.filter(ClubActivity.priority == priority)
    if assignee_id is not None:
        query = query.filter(ClubActivity.assignee_id == assignee_id)
    if search:
        query = query.filter(ClubActivity.title.ilike(f"%{search}%"))

    total = query.count()

    sort_column = ALLOWED_SORT_FIELDS.get(sort_by, ClubActivity.created_at)
    query = query.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())

    items = query.offset((page - 1) * size).limit(size).all()

    return items, total
#endregion

# region ================================ Xem chi tiết hoạt đông của CLB đó ================================
def get_activity(db: Session, activity_id: int) -> ClubActivity:
    activity = db.query(ClubActivity).filter(ClubActivity.id == activity_id).first()
    if activity is None:
        raise NotFoundException("Hoạt động không tồn tại")

    #
    #
    #
    club = db.query(Club).filter(Club.id == activity.club_id).first()
    if club is None or club.is_deleted or club.deleted_at is not None:
        raise NotFoundException("Hoạt động không tồn tại")
    
    return activity


def get_activity_detail(db: Session, activity_id: int, actor: User) -> ClubActivity:
    activity = get_activity(db, activity_id)
    # Kiểm tra user thuộc club của hoạt động trước khi trả dữ liệu
    require_member(db, activity.club_id, actor.id)
    return activity
#endregion

# region ================================ Cập nhật tt hoạt đông của CLB đó ================================
def update_activity(db: Session, activity: ClubActivity, data: ClubActivityUpdate, actor: User) -> ClubActivity:
    membership = require_member(db, activity.club_id, actor.id)
    is_owner = membership.role == ClubMemberRole.OWNER
    is_assignee = activity.assignee_id is not None and activity.assignee_id == actor.id

    # Permission: chỉ Owner của club hoặc assignee đang được gán mới được sửa
    if not (is_owner or is_assignee):
        raise ForbiddenException("Bạn không có quyền cập nhật hoạt động này")

    # exclude_unset để không ghi đè trường không được gửi lên
    update_data = data.model_dump(exclude_unset=True)

    #
    #
    #
    if update_data.get("assignee_id") is None:
        update_data.pop("assignee_id", None)

    if "assignee_id" in update_data and not is_owner:
        raise ForbiddenException("Chỉ Owner mới có thể gán lại người phụ trách")

    #
    #
    # if is_assignee and not is_owner:
    #     not_allowed_fields = set(update_data.keys()) - {"status"}
    #     if not_allowed_fields:
    #         raise ForbiddenException(
    #             "Người được gán chỉ được phép cập nhật trạng thái (status) của hoạt động"
    #         )

    if update_data.get("assignee_id") is not None:
        validate_assignee(db, activity.club_id, update_data["assignee_id"])

    changes = []
    for field, value in update_data.items():
        setattr(activity, field, value)
        changes.append(field)

    try:
        db.add(activity)
        db.flush()
        if changes:
            db.add(ClubLog(
                club_id=activity.club_id,
                actor_id=actor.id,
                action="UPDATE_ACTIVITY",
                details=f"Cập nhật hoạt động #{activity.id}: {', '.join(changes)}",
            ))
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
        db.refresh(activity)

    return activity
#endregion

# region ================================ Xóa hoạt động của CLB đó ================================
def delete_activity(db: Session, activity: ClubActivity, actor: User) -> None:
    # Chỉ Owner của club mới được xóa hoạt động
    require_owner(db, activity.club_id, actor.id)

    club_id = activity.club_id
    activity_title = activity.title

    try:
        attachments = db.query(ActivityAttachment).filter(ActivityAttachment.activity_id == activity.id).all()
        for attachment in attachments:
            Path(attachment.file_path).unlink(missing_ok=True)

        db.query(ActivityAttachment).filter(ActivityAttachment.activity_id == activity.id).delete()
        db.query(ActivityComment).filter(ActivityComment.activity_id == activity.id).delete()
        db.delete(activity)
        db.add(ClubLog(
            club_id=club_id,
            actor_id=actor.id,
            action="DELETE_ACTIVITY",
            details=f"Xóa hoạt động: {activity_title}",
        ))
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
#endregion

# region ================================ Thêm comment hoạt động của CLB đó ================================
def add_comment(
    db: Session,
    activity: ClubActivity,
    content: str,
    actor: User,
) -> ActivityComment:
    require_member(db, activity.club_id, actor.id)
    comment = ActivityComment(
        activity_id=activity.id,
        user_id=actor.id,
        content=content.strip(),
    )
    if not comment.content:
        raise BadRequestException("Nội dung comment không được để trống")

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

#endregion

# region ================================ Xem list comment hoạt động của CLB đó ================================
def list_comments(db: Session,activity: ClubActivity,actor: User) -> list[ActivityComment]:
    require_member(db, activity.club_id, actor.id)
    return (
        db.query(ActivityComment)
        .filter(ActivityComment.activity_id == activity.id)
        .order_by(ActivityComment.created_at.asc(), ActivityComment.id.asc())
        .all()
    )
#endregion

# region ================================ Lưu file đính kèm hoạt động của CLB đó ================================
def save_attachment(
    db: Session,
    activity: ClubActivity,
    upload: UploadFile,
    actor: User,
) -> ActivityAttachment:
    require_member(db, activity.club_id, actor.id)

    extension = ALLOWED_ATTACHMENT_TYPES.get(upload.content_type or "")
    if extension is None:
        raise BadRequestException("Chỉ hỗ trợ JPG, PNG, WEBP hoặc PDF")

    content = upload.file.read(MAX_ATTACHMENT_SIZE + 1)
    if len(content) > MAX_ATTACHMENT_SIZE:
        raise BadRequestException("File đính kèm không được vượt quá 5 MB")
    if not content:
        raise BadRequestException("File đính kèm không được rỗng")

    stored_name = f"{uuid4().hex}{extension}"
    ATTACHMENT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file_path = ATTACHMENT_DIRECTORY / stored_name
    file_path.write_bytes(content)

    attachment = ActivityAttachment(
        activity_id=activity.id,
        user_id=actor.id,
        original_name=upload.filename or stored_name,
        stored_name=stored_name,
        content_type=upload.content_type or "application/octet-stream",
        file_size=len(content),
        file_path=str(file_path),
    )
    try:
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise
    return attachment
#endregion


# region ================================ Xem file đính kèm hoạt động của CLB đó ================================
def list_attachments(
    db: Session,
    activity: ClubActivity,
    actor: User,
) -> list[ActivityAttachment]:
    require_member(db, activity.club_id, actor.id)
    return (
        db.query(ActivityAttachment)
        .filter(ActivityAttachment.activity_id == activity.id)
        .order_by(ActivityAttachment.created_at.desc(), ActivityAttachment.id.desc())
        .all()
    )
#endregion












