class AppException(Exception):
    """Base application exception — NOT an HTTPException.
    Caught at the route layer and converted to an HTTP response."""

    def __init__(self, message: str = "Internal server error", code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)


class NotAuthorizedException(AppException):
    def __init__(self, message: str = "User not authorized"):
        super().__init__(message=message, code=401)


class AccessDeniedException(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, code=403)


class InvalidTokenException(AppException):
    def __init__(self, message: str = "Token is invalid"):
        super().__init__(message=message, code=401)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code=404)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code=400)


class TicketAlreadyScannedException(AppException):
    def __init__(self, message: str = "Ticket already scanned"):
        super().__init__(message=message, code=422)


class TicketCancelledException(AppException):
    def __init__(self, message: str = "Ticket is cancelled"):
        super().__init__(message=message, code=422)
