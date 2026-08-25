class AppException(Exception):
    status_code: int = 500
    error: str = "Internal Server Error"
    message: str = "Internal server error"

    def __init__(self, message: str = None):
        self.message = message or self.message
        # super().__init__(self.message)


class BadRequestException(AppException):
    status_code = 400
    error = "Bad Request"
    message = "Bad request"

class UnauthorizedException(AppException):
    status_code = 401
    error = "Unauthorized error"
    message = "Unauthorized error"

class ForbiddenException(AppException):
    status_code = 403
    error = "Forbidden"
    message = "Forbidden"


class NotFoundException(AppException):
    status_code = 404
    error = "Resource not found"
    message = "Resource not found"

class HTTPConflict(AppException):
    status_code = 409
    error = "HTTP 409 Conflict"
    message = "HTTP 409 Conflict"

class TooManyRequestsException(AppException):
    status_code = 429 
    error = "Too Many Requests"
    message = "Too Many Requests"
