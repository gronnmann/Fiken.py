# Different exceptions

class RequestErrorException(Exception):
    """Parent class for all ways a Request can fail."""
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


class RequestMethodNotAllowedException(RequestErrorException):
    """Raised when the response is 405 Method Not Allowed or method is not allowed."""
    pass


class RequestWrongMediaTypeException(RequestErrorException):
    """Raised when the response is 415 Unsupported Media Type."""
    pass
