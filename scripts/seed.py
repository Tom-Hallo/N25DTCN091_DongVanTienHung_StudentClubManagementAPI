import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.db.database import Base, sessionLocal, engine
from app.models.activity import (
    ClubActivity,
    ActivityStatus,
    ActivityPriority,
)
from app.models.club import (
    Club,
    ClubMember,
    ClubMemberRole,
)
from app.models.user import User, RoleClassify


def seed():
    Base.metadata.create_all(bind=engine)

    db = sessionLocal()

    try:
        # =========================
        # 1. USERS
        # =========================

        admin = User(
            email="admin@club.edu.vn",
            password_hash=hash_password("Admin@123"),
            full_name="Quan Tri Vien",
            role=RoleClassify.ADMIN,
        )

        user1 = User(
            email="minhanh@club.edu.vn",
            password_hash=hash_password("User@123"),
            full_name="Nguyen Minh Anh",
            role=RoleClassify.USER,
        )

        user2 = User(
            email="tuanhung@club.edu.vn",
            password_hash=hash_password("User@123"),
            full_name="Tran Tuan Hung",
            role=RoleClassify.USER,
        )

        db.add_all([admin, user1, user2])
        db.flush()

        # =========================
        # 2. CLUB
        # =========================

        club = Club(
            name="CLB Lap Trinh",
            description="Cau lac bo danh cho sinh vien yeu thich lap trinh va cong nghe",
            owner_id=user1.id,
        )

        db.add(club)
        db.flush()

        # =========================
        # 3. CLUB MEMBERS
        # =========================

        owner = ClubMember(
            club_id=club.id,
            user_id=user1.id,
            role=ClubMemberRole.OWNER,
        )

        member = ClubMember(
            club_id=club.id,
            user_id=user2.id,
            role=ClubMemberRole.MEMBER,
        )

        db.add_all([owner, member])
        db.flush()

        # =========================
        # 4. ACTIVITIES
        # =========================

        activity1 = ClubActivity(
            club_id=club.id,
            title="Workshop FastAPI can ban",
            description="Buoi workshop huong dan xay dung API voi FastAPI va SQLAlchemy",
            assignee_id=user1.id,
            status=ActivityStatus.TODO,
            priority=ActivityPriority.HIGH,
            due_date=datetime.now() + timedelta(days=7),
        )

        activity2 = ClubActivity(
            club_id=club.id,
            title="Giao luu tan sinh vien",
            description="Su kien gioi thieu CLB toi cac ban sinh vien nam nhat",
            assignee_id=user2.id,
            status=ActivityStatus.IN_PROGRESS,
            priority=ActivityPriority.MEDIUM,
            due_date=datetime.now() + timedelta(days=14),
        )

        db.add_all([activity1, activity2])
        db.flush()

    except Exception as exc:
        db.rollback()
        print(f"Seed du lieu that bai: {exc}")

    else:
        db.commit()

        print("Seed du lieu mau thanh cong:")
        print("  - 3 users (1 admin, 2 user)")
        print(f"  - 1 club: {club.name}")
        print("  - 2 thanh vien club")
        print("  - 2 hoat dong club")

    finally:
        db.close()


if __name__ == "__main__":
    seed()