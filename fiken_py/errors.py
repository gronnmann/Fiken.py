# Different exceptions


class RequestErrorException(Exception):
    """Parent class for all ways a Request can fail."""

    def __init__(self, exception, error_base=None, error_description=None):
        super().__init__(exception)
        self.error_base = error_base
        self.error_details = error_description

    def __str__(self):
        if self.error_details:
            if self.error_base:
                return f"{super().__str__()} ({self.error_base}: {self.error_details})"
            else:
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
