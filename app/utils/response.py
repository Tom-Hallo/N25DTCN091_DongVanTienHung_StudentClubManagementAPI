from datetime import datetime, timezone


def api_response(
    status_code: int,
    data: dict | None = None,
    message: str = "Thành công",
    error: str | None = None,
    path: str | None = None,
) -> dict | None:
    return {
        "status_code": status_code,
        "error": error,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": path,
    }


def error_response(
    status_code: int,
    error: str,
    message: str,
    path: str | None = None,
    details: list | dict | None = None,
) -> dict | None:
    return api_response(
        status_code=status_code,
        error=error,
        message=message,
        data={"details": details} if details is not None else None,
        path=path,
    )
