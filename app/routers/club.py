from fastapi import APIRouter, status, Form, Depends, Query, Request
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
@router.post("",response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_a_club(
    data: ClubCreateForm = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):

    club_data = ClubCreate(name=data.name,description=data.description,owner_id=current_user.id)
    new_club = club_service.create_club(db=db, club_data=club_data, actor_id=current_user.id)

    return new_club
#endregion
    
# region ================================ Xem club mình tham gia ================================
@router.get("")
def view_my_clubs(
    search: str = Query(default=None, description="Tìm theo tên câu lạc bộ"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    list_clubs = club_service.list_user_clubs(db, current_user.id, search=search) 
    
    return list_clubs
#endregion

# region ================================ Xem club qua id ================================
@router.get("/{id}", response_model=ClubResponse)
def view_my_clubs_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_member(db, id, current_user.id)
    return club
#endregion

# region ================================ Thêm tv club (Owner) ================================
@router.post("/{id}/members", status_code=status.HTTP_201_CREATED)
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
@router.put("/{id}", response_model=ClubResponse)
def update_club_all_infor(
    id: int,
    data: ClubPutUpdate = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    return club_service.update_club(db, club, data.name, data.description, current_user.id)


@router.patch("/{id}", response_model=ClubResponse)
def update_club_specific_info(
    id: int,
    data: ClubUpdate = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, id)
    club_service.require_owner(db, id, current_user.id)
    return club_service.update_club(db, club, data.name, data.description, current_user.id)
#endregion

# region================================ Xóa tt club (Owner) ================================
@router.delete("/{id}", status_code=status.HTTP_200_OK)
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
@router.delete("/{id}/members/{user_id}", status_code=status.HTTP_200_OK)
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
@router.get("/{id}/members", status_code=status.HTTP_200_OK )
def list_members_club(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club_service.get_club(db, id)
    club_service.require_member(db, id, current_user.id)

    club_members = club_service.list_members(db, id) 

    return club_members
#endregion