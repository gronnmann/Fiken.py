from typing import Optional

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class BalanceAccount(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/accounts/{accountCode}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/accounts/'

    code: Optional[str] = None
    name: Optional[str] = None

    @property
    def id_attr(self):
        return "accountCode", self.code