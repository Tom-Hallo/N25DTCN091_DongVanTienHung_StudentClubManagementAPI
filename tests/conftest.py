import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.models.user import User, RoleClassify
from app.routers import auth, club, users, activity
from app.utils.exceptions import AppException
from app.utils.response import error_response
from app.core.security import hash_password


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False)
    session = session_factory()

    owner = User(
        email="owner@example.com",
        password_hash=hash_password("password123"),
        full_name="Club Owner",
        role=RoleClassify.USER,
    )
    member = User(
        email="member@example.com",
        password_hash=hash_password("password123"),
        full_name="Club Member",
        role=RoleClassify.USER,
    )
    admin = User(
        email="admin@example.com",
        password_hash=hash_password("password123"),
        full_name="System Admin",
        role=RoleClassify.ADMIN,
    )
    session.add_all([owner, member, admin])
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    test_app = FastAPI()
    test_app.include_router(auth.router)
    test_app.include_router(users.router)
    test_app.include_router(club.router)
    test_app.include_router(activity.router)

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    @test_app.exception_handler(AppException)
    def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.status_code, exc.error, exc.message, request.url.path),
        )

    @test_app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        details = [
            {
                "field": ".".join(str(part) for part in err.get("loc", []) if part != "body"),
                "message": err.get("msg"),
                "type": err.get("type"),
            }
            for err in errors
        ]
        message = errors[0]["msg"] if errors else "Lỗi xác thực dữ liệu"
        return JSONResponse(
            status_code=422,
            content=error_response(422, "Lỗi xác thực dữ liệu", message, request.url.path, details),
        )

    with TestClient(test_app) as test_client:
        yield test_client


def login(client: TestClient, email: str = "owner@example.com") -> str:
    response = client.post(
        "/auth/login",
        data={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
