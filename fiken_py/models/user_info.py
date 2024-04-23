from typing import Optional

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class UserInfo(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/user'

    name: Optional[str] = None
    email: Optional[str] = None

