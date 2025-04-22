import logging
from urllib import response

from requests import HTTPError


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


    if err:
        logging.error(f"Error: {err}")
    if err_description:
        logging.error(f"Error description: {err_description}")