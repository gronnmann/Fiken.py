from datetime import date
from typing import Optional, ClassVar

from pydantic import BaseModel, model_validator

from fiken_py.fiken_object import FikenObject, T, FikenObjectRequest
from fiken_py.fiken_types import BankAccountType


class BankAccountBase(BaseModel):
    name: str
    bankAccountNumber: str
    bic: Optional[str] = None
    iban: Optional[str] = None
    foreignService: Optional[str] = None
    type: BankAccountType
    inactive: bool = False


class BankAccount(BankAccountBase, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/bankAccounts/{bankAccountId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/bankAccounts/'

    bankAccountId: Optional[int] = None
    accountCode: str = None
    reconciledBalance: int = None
    reconciledDate: Optional[date] = None  # TODO - new date type

    # TODO - validate foreign

    # @model_validator(mode='after')
    # def check_foreign_service(cls, values):
    #     if values.get('type') == BankAccountType.FOREIGN and not values.get('foreignService'):
    #         raise ValueError('foreignService must be provided for foreign bank accounts')


class BankAccountCreateRequest(BankAccountBase, FikenObjectRequest):
    BASE_CLASS: ClassVar[FikenObject] = BankAccount

    _POST_PATH = '/companies/{companySlug}/bankAccounts/'
