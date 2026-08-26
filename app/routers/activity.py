from fastapi import APIRouter, status, Request, Form, Depends, Query, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.user import User
from app.db.database import get_db
from app.schemas.activity import (
    ClubActivityCreateForm,
    ClubActivityResponse,
    ClubActivityUpdate,
    ActivityPriority,
    ActivityStatus,
    ActivityCommentCreate,
    ActivityCommentResponse,
    ActivityAttachmentResponse,
)
from app.services import club_service
from app.services import activity_service
from app.utils.response import api_response
from app.dependencies.dependencies import get_current_user

router = APIRouter(tags=["Activity"])

# region================================ Tạo hoạt đông CLB (Mem/Own) ================================
@router.post(
    "/clubs/{id}/activities",
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hoạt động câu lạc bộ",
    description="Thành viên tạo một hoạt động trong câu lạc bộ.",
)
def create_activity(
    id: int,
    request: Request,
    data: ClubActivityCreateForm = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club_service.get_club(db, id)
    new_activity = activity_service.create_activity(db, club_id=id, data=data, actor=current_user)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=api_response(
            status_code=status.HTTP_201_CREATED,
            message="Tạo hoạt động thành công",
            data=ClubActivityResponse.model_validate(new_activity).model_dump(mode="json"),
            path=request.url.path,
        ),
    )

#endregion

# region================================ Xem các hoạt đông của CLB đó ================================
@router.get(
    "/clubs/{id}/activities", status_code=status.HTTP_200_OK,
    summary="Danh sách hoạt động câu lạc bộ",
    description="Lọc, tìm kiếm, sắp xếp và phân trang hoạt động của câu lạc bộ.",
)
def list_club_activities(
    id: int,
    request: Request,
    status_filter: ActivityStatus | None = Query(default=None, alias="status", description="Lọc theo trạng thái"),
    priority: ActivityPriority | None = Query(default=None, description="Lọc theo độ ưu tiên"),
    assignee_id: int | None = Query(default=None, description="Lọc theo người phụ trách"),
    search: str | None = Query(default=None, description="Tìm theo tiêu đề"),
    sort_by: str  = Query(default="created_at", description="created_at hoặc due_date"), #chưa validate nếu như nhập không đúng 
    sort_order: str = Query(default="desc", description="asc hoặc desc"), # như trên
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club_service.get_club(db, id)
    items, total = activity_service.list_activities(db,club_id=id,actor=current_user,status=status_filter,priority=priority,
        assignee_id=assignee_id,search=search,sort_by=sort_by,sort_order=sort_order,page=page,size=size,)

    items_response = [ClubActivityResponse.model_validate(item).model_dump(mode="json") for item in items]
    total_pages = (total + size - 1) // size if size else 0

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Đã trích xuất hoạt động thành công",
            data={
                "items": items_response,
                "meta": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "total_pages": total_pages,
                },
            },
            path=request.url.path,
        ),
    )

#endregion

# region================================ Xem chi tiết hoạt đông của CLB đó ================================
@router.get(
    "/activities/{id}",
    summary="Chi tiết hoạt động",
    description="Xem chi tiết hoạt động nếu người dùng thuộc câu lạc bộ.",
)
def get_activity_detail(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    activity = activity_service.get_activity_detail(db, activity_id=id, actor=current_user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Lấy thông tin hoạt động thành công",
            data=ClubActivityResponse.model_validate(activity).model_dump(mode="json"),
            path=request.url.path,
        ),
    )
#endregion

# region================================ Cập nhật tt hoạt đông của CLB đó ================================
@router.patch("/activities/{id}",
    summary="Cập nhật hoạt động",
    description="Owner hoặc assignee cập nhật các trường được gửi lên.",
)
def update_activity(
    id: int,
    request: Request,
    data: ClubActivityUpdate = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = activity_service.get_activity(db, id)
    updated_activity = activity_service.update_activity(db, activity=activity, data=data, actor=current_user)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Cập nhật hoạt động thành công",
            data=ClubActivityResponse.model_validate(updated_activity).model_dump(mode="json"),
            path=request.url.path,
        ),
    )
#endregion

# region================================ Xóa hoạt động của CLB đó ================================
@router.delete(
    "/activities/{id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa hoạt động",
    description="Owner xóa hoạt động khỏi câu lạc bộ.",
)
def delete_activity(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = activity_service.get_activity(db, id)
    activity_service.delete_activity(db, activity=activity, actor=current_user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Xóa hoạt động thành công",
            path=request.url.path,
        ),
    )
#endregion


@router.post(
    "/activities/{id}/comments",
    status_code=status.HTTP_201_CREATED,
    summary="Thêm comment cho hoạt động",
    description="Chỉ thành viên của câu lạc bộ được tạo comment.",
)
def create_activity_comment(
    id: int,
    request: Request,
    data: ActivityCommentCreate = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = activity_service.get_activity(db, id)
    comment = activity_service.add_comment(
        db, activity, data.content, current_user
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=api_response(
            status_code=status.HTTP_201_CREATED,
            message="Thêm comment thành công",
            data=ActivityCommentResponse.model_validate(comment).model_dump(mode="json"),
            path=request.url.path,
        ),
    )


@router.get(
    "/activities/{id}/comments",
    status_code=status.HTTP_200_OK,
    summary="Xem comment của hoạt động",
    description="Chỉ thành viên của câu lạc bộ được xem comment.",
)
def get_activity_comments(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = activity_service.get_activity(db, id)
    comments = activity_service.list_comments(db, activity, current_user)
    data = [
        ActivityCommentResponse.model_validate(comment).model_dump(mode="json")
        for comment in comments
    ]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Lấy comment thành công",
            data=data,
            path=request.url.path,
        ),
    )


@router.post(
    "/activities/{id}/attachments",
    status_code=status.HTTP_201_CREATED,
    summary="Upload file cho hoạt động",
    description="Chỉ thành viên được upload JPG, PNG, WEBP hoặc PDF tối đa 5 MB.",
)
def upload_activity_attachment(
    id: int,
    request: Request,
    file: UploadFile = File(..., description="File tối đa 5 MB"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = activity_service.get_activity(db, id)
    attachment = activity_service.save_attachment(
        db, activity, file, current_user
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=api_response(
            status_code=status.HTTP_201_CREATED,
            message="Upload file thành công",
            data=ActivityAttachmentResponse.model_validate(attachment).model_dump(mode="json"),
            path=request.url.path,
        ),
    )


@router.get(
    "/activities/{id}/attachments",
    status_code=status.HTTP_200_OK,
    summary="Xem file đính kèm",
    description="Chỉ thành viên của câu lạc bộ được xem file đính kèm.",
)
def get_activity_attachments(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = activity_service.get_activity(db, id)
    attachments = activity_service.list_attachments(db, activity, current_user)
    data = [
        ActivityAttachmentResponse.model_validate(item).model_dump(mode="json")
        for item in attachments
    ]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Lấy file đính kèm thành công",
            data=data,
            path=request.url.path,
        ),
    )
