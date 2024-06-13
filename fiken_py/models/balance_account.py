import datetime
import typing
from typing import Optional, Any

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, OptionalAccessToken


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

    @classmethod
    def getAll(
        cls,
        token: OptionalAccessToken = None,
        follow_pages: bool = True,
        page: Optional[int] = None,
        date: datetime.date = datetime.date.today(),
        **kwargs: Any,
    ) -> list[typing.Self]:
        return super().getAll(
            token=token, follow_pages=follow_pages, page=page, date=date, **kwargs
        )
