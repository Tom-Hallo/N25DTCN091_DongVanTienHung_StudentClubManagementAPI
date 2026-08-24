from fastapi import APIRouter, status, Form, Depends, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.db.database import get_db
from app.services import club_service
from app.schemas.club import ClubCreate, ClubResponse, ClubMemberResponse, ClubMemberCreate, ClubUpdate
from app.dependencies.dependencies import get_current_user

router = APIRouter(prefix="/clubs" , tags=["Clubs"])

#Tạo club
@router.post("",response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_a_club(
    name_club: str = Form(..., description="Nhập tên clb"),
    description: str = Form(..., description="Nhập mô tả clb"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):

    club_data = ClubCreate(name=name_club, description=description, owner_id=current_user.id)
    new_club = club_service.create_club(db=db, club_data=club_data)

    return new_club
    
#Xem clb mình tham gia
@router.get("")
def view_my_clubs(
    search: str = Query(default=None, description="Tìm theo tên câu lạc bộ"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    list_clubs = club_service.list_user_clubs(db, current_user.id, search=search) 
    
    return list_clubs

#Xem club qua id
@router.get("/{club_id}", response_model=ClubResponse)
def view_my_clubs_by_id(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, club_id)
    club_service.require_member(db, club_id, current_user.id)
    return club

#Thêm tv club
@router.post("/{club_id}/members",response_model=ClubMemberResponse,status_code=status.HTTP_201_CREATED)
def add_member_club(
    club_id: int,
    user_id: int = Form(..., description="Nhập ID user để thêm vào"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    data = ClubMemberCreate(user_id=user_id, club_id=club_id)
    
    club_service.get_club(db, club_id)
    club_service.require_owner(db, club_id, current_user.id)
    return club_service.add_member(db, club_id, data.user_id)

#Sửa/Xóa - dành cho owner
@router.put("/{club_id}", response_model=ClubResponse)
@router.patch("/{club_id}", response_model=ClubResponse)
def update_club_endpoint(
    club_id: int,
    data: ClubUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, club_id)
    club_service.require_owner(db, club_id, current_user.id)
    return club_service.update_club(db, club, data.name, data.description)


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club_endpoint(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club(db, club_id)
    club_service.require_owner(db, club_id, current_user.id)
    club_service.delete_club(db, club)

