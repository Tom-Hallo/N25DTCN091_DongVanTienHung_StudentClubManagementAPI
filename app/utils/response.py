from datetime import datetime, timezone
from typing import Any


def api_response(
    status_code: int,
    data: Any = None,
    message: str = "Thành công",
    error: str | None = None,
    path: str | None = None,
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    return api_response(
        status_code=status_code,
        error=error,
        message=message,
        path=path,
    )
