from pydantic import BaseModel

class ErrorDetail(BaseModel):
    code: int
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

def error_response(status_code: int, message: str) -> dict[str | None]:
    return ErrorResponse(error=ErrorDetail(code=status_code, message=message)).model_dump()
