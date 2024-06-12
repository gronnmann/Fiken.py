import datetime
from typing import Optional

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class BalanceAccount(BaseModel, FikenObject):
    _GET_PATH_SINGLE = "/companies/{companySlug}/accounts/{accountCode}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/accounts/"

    code: Optional[str] = None
    name: Optional[str] = None

    def get_balance(self, date: datetime.date = datetime.date.today()):
        return BalanceAccountBalance.get(accountCode=self.code, date=date)

    @property
    def id_attr(self):
        return "accountCode", self.code


class BalanceAccountBalance(BalanceAccount):
    _GET_PATH_SINGLE = "/companies/{companySlug}/accountBalances/{accountCode}/"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/accountBalances/"

    balance: Optional[int] = None
