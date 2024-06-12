import logging
from urllib import response

from requests import HTTPError

from fiken_py.errors import (
    RequestBadRequestException,
    RequestUserUnauthenticatedException,
    RequestForbiddenException,
    RequestContentNotFoundException,
    RequestUnsupportedMethodException,
    RequestWrongMediaTypeException,
    RequestErrorException,
)


def handle_error(e: HTTPError):
    logging.error(f"Request HTTP failed: {e}")

    err = None
    err_description = None
    try:
        json = e.response.json()
        if json.get("error"):
            err = json["error"]
        if json.get("error_description") is not None:
            err_description = json["error_description"]
        elif json.get("message") is not None:
            err_description = (
                json["message"]
                if err_description is None
                else f"{err_description}: {json['message']}"
            )
        else:
            err = "Unparsed error"
            err_description = e.response.text
    except Exception:
        err = "Unparsed error"
        err_description = e.response.text

    if e.response.status_code == 400:
        raise RequestBadRequestException(e, err, err_description)
    elif e.response.status_code == 401:
        raise RequestUserUnauthenticatedException(e, err, err_description)
    elif e.response.status_code == 403:
        raise RequestForbiddenException(e, err, err_description)
    elif e.response.status_code == 404:
        raise RequestContentNotFoundException(e, err, err_description)
    elif e.response.status_code == 405:
        raise RequestUnsupportedMethodException(e, err, err_description)
    elif e.response.status_code == 415:
        raise RequestWrongMediaTypeException(e, err, err_description)
    else:
        raise RequestErrorException(e, err, err_description)
