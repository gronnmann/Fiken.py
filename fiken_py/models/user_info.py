from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class UserInfo(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/user'
    _GET_PATH_MULTIPLE = None

    name: str
    email: str

