import logging
import os
import uuid
import random

import dotenv
import pytest

from fiken_py.fiken_object import FikenObject


@pytest.fixture(autouse=True)
def set_auth_token():
    dotenv.load_dotenv("test_online/.env")

    FikenObject.set_auth_token(os.getenv("FIKEN_API_TOKEN"))
    FikenObject.set_company_slug(os.getenv("FIKEN_COMPANY_SLUG"))

@pytest.fixture(autouse=True)
def set_logger_level():
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="session")
def unique_id() -> str:
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choices(abc, k=4))