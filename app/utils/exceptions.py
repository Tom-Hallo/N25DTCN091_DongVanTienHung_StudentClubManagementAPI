class AppException(Exception):
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str = None):
        self.message = message or self.message
        # super().__init__(self.message)

class BadRequestException(AppException):
    status_code = 400
    message = "Bad request"


class ForbiddenException(AppException):
    status_code = 403
    message = "Forbidden"


class NotFoundException(AppException):
    status_code = 404
    message = "Resource not found"

class UnauthorizedException(AppException):
    status_code = 401
    message = "Unauthorized error"

class TooManyRequestsException(AppException):
    status_code = 429 
    message = "Too Many Requests"
