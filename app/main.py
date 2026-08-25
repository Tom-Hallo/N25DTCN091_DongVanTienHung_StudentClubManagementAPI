from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db.database import Base, engine, ensure_club_soft_delete_column
# from app.models import user,club,activity,club_log
from app.utils.response import error_response
from app.utils.exceptions import AppException
from app.routers import auth, users, club, activity

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(club.router)
app.include_router(activity.router)

Base.metadata.create_all(bind=engine)
ensure_club_soft_delete_column()

@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.status_code, exc.error, exc.message, request.url.path),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(
            422, "Lỗi xác thực dữ liệu", exc.errors()[0]["msg"], request.url.path
        ),
    )


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            exc.status_code, "HTTP error", str(exc.detail), request.url.path
        ),
    )


@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=error_response(
            500, "Internal server error", "Đã xảy ra lỗi máy chủ", request.url.path
        ),
    )

@app.get("/health-checking")
def get_health():
    return {
        "message": "API đang chạy ngon lành"
    }

