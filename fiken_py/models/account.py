from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class Account(BaseModel, FikenObject):
    # TODO - maybe change to AccountBalance
    _GET_PATH_SINGLE = '/companies/{companySlug}/accounts/{accountCode}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/accounts/'

    code: str
    name: str

    # TODO - change all things to optional?