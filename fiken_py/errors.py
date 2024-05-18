# Different exceptions

class RequestErrorException(Exception):
    """Parent class for all ways a Request can fail."""
    def __init__(self, err, error_details):
        super().__init__(err)
        self.error_details = error_details

    def __str__(self):
        if self.error_details:
            return f"{super().__str__()} ({self.error_details})"
        else:
            return super().__str__()


class RequestConnectionException(RequestErrorException):
    """Raised when the connection to the API fails."""
    pass


class RequestBadRequestException(RequestErrorException):
    """Raised when the response is 400 Bad Request."""
    pass


class RequestUserUnauthenticatedException(RequestErrorException):
    """Raised when the response is 401 - user not authenticated."""
    pass


class RequestForbiddenException(RequestErrorException):
    """Raised when the response is 403 Forbidden."""
    pass


class RequestContentNotFoundException(RequestErrorException):
    """Raised when the response is 404 Not Found."""
    pass


class RequestUnsupportedMethodException(RequestErrorException):
    """Raised when the response is 405 Method Not Allowed or method fails pre-check."""
    pass


class RequestWrongMediaTypeException(RequestErrorException):
    """Raised when the response is 415 Unsupported Media Type."""
    pass