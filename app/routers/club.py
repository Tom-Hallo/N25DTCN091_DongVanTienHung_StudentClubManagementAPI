from fastapi import APIRouter, status, Form, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.user import User
from app.db.database import get_db
from app.services import club_service
from app.schemas.club import ClubCreate, ClubResponse, ClubMemberResponse, ClubMemberCreate, ClubUpdate, ClubPutUpdate, ClubCreateForm, ClubLogResponse
from app.dependencies.dependencies import get_current_user
from app.utils.response import api_response

router = APIRouter(prefix="/clubs" , tags=["Clubs"])

# region ================================ Tạo club ================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Tạo câu lạc bộ",
    description="Tạo một câu lạc bộ mới và gán người dùng hiện tại làm owner.",
)
def create_a_club(
    request: Request,
    data: ClubCreateForm = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):

    club_data = ClubCreate(name=data.name,description=data.description,owner_id=current_user.id)
    new_club = club_service.create_club(db=db, club_data=club_data, actor_id=current_user.id)

    # return new_club

    club_Response = ClubResponse.model_validate(new_club).model_dump(mode="json")

    return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=api_response(
                status_code=status.HTTP_201_CREATED,
                message="Đã thêm câu lạc bộ thành công",
                data=club_Response,
                path=request.url.path,
            ),
        )
#endregion
    
# region ================================ Xem club mình tham gia ================================
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Danh sách câu lạc bộ",
    description="Lấy các câu lạc bộ mà người dùng hiện tại đang tham gia.",
)
def view_my_clubs(
    request: Request,
    search: str = Query(default=None, description="Tìm theo tên câu lạc bộ"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    list_clubs = club_service.list_user_clubs(db, current_user.id, search=search) 

    # list_clubs_response = ClubResponse.model_validate(list_clubs).model_dump(mode="json")

    list_clubs_response = [
    ClubResponse.model_validate(club).model_dump(mode="json")
    for club in list_clubs
    ]
    
    # return list_clubs

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_201_CREATED,
            message="Đã trích xuất câu lạc bộ thành công",
            data=list_clubs_response,
            path=request.url.path,
        ),
    )
#endregion

# region ================================ Xem club qua id ================================
@router.get(
    "/{id}",
    summary="Chi tiết câu lạc bộ",
    description="Lấy thông tin câu lạc bộ mà người dùng là thành viên.",
)
def view_my_clubs_by_id(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_member(db, id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Lấy thông tin câu lạc bộ thành công",
            data=ClubResponse.model_validate(club).model_dump(mode="json"),
            path=request.url.path,
        ),
    )
#endregion

# region ================================ Thêm tv club (Owner) ================================
@router.post(
    "/{id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên",
    description="Owner thêm một user vào câu lạc bộ.",
)
def add_member_club(
    id: int,
    request: Request,
    user_id: int = Form(..., description="Nhập ID user để thêm vào"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    data = ClubMemberCreate(user_id=user_id, club_id=id)
    
    club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    member = club_service.add_member(db, id, data.user_id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=api_response(
            status_code=status.HTTP_201_CREATED,
            message="Thêm thành viên thành công",
            data=ClubMemberResponse.model_validate(member).model_dump(mode="json"),
            path=request.url.path,
        ),
    )
#endregion

# region ================================ Sửa tt club (Owner) ================================
@router.put(
    "/{id}",
    summary="Cập nhật toàn bộ câu lạc bộ",
    description="Owner cập nhật thông tin câu lạc bộ.",
)
def update_club_all_infor(
    id: int,
    request: Request,
    data: ClubPutUpdate = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    updated_club = club_service.update_club(
        db, club, data.name, data.description, current_user.id
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Cập nhật câu lạc bộ thành công",
            data=ClubResponse.model_validate(updated_club).model_dump(mode="json"),
            path=request.url.path,
        ),
    )


@router.patch(
    "/{id}",
    summary="Cập nhật một phần câu lạc bộ",
    description="Owner cập nhật các trường được gửi lên.",
)
def update_club_specific_info(
    id: int,
    request: Request,
    data: ClubUpdate = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    updated_club = club_service.update_club(
        db, club, data.name, data.description, current_user.id
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Cập nhật câu lạc bộ thành công",
            data=ClubResponse.model_validate(updated_club).model_dump(mode="json"),
            path=request.url.path,
        ),
    )
#endregion

# region================================ Xóa tt club (Owner) ================================
@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa câu lạc bộ",
    description="Đánh dấu câu lạc bộ đã bị xóa mà không mất dữ liệu.",
)
def delete_club(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    club_service.delete_club(db, club, current_user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Xóa câu lạc bộ thành công",
            path=request.url.path,
        ),
    )
#endregion

# region================================ Xóa tv club (Owner) ================================
@router.delete(
    "/{id}/members/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên",
    description="Owner xóa một thành viên khỏi câu lạc bộ.",
)
def remove_member(
    id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    club_service.remove_member(db, id, user_id, current_user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Xóa thành viên thành công",
            path=request.url.path,
        ),
    )
#endregion

# region================================ Xem members trong club ================================
@router.get(
    "/{id}/members",
    status_code=status.HTTP_200_OK,
    summary="Danh sách thành viên",
    description="Lấy danh sách thành viên của câu lạc bộ.",
)
def list_members_club(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club_service.get_club(db, id)
    club_service.require_member(db, id, current_user.id)

    club_members = club_service.list_members(db, id) 

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=api_response(
            status_code=status.HTTP_200_OK,
            message="Lấy danh sách thành viên thành công",
            data=jsonable_encoder(club_members),
            path=request.url.path,
        ),
    )
#endregion