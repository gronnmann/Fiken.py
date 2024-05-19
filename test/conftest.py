import pytest

from fiken_py.fiken_object import FikenObject


@pytest.fixture(autouse=True, scope="session")
def disable_rate_limit():
    FikenObject.set_rate_limit(False)
