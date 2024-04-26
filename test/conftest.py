import pytest

from fiken_py.fiken_object import FikenObject


@pytest.fixture(autouse=True, scope="session")
def set_auth_token():
    FikenObject.set_rate_limit(False)
