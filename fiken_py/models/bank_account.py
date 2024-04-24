from datetime import date
from typing import Optional, ClassVar

from pydantic import BaseModel, model_validator, Field

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

    name: Optional[str] = None
    bankAccountNumber: Optional[str] = None
    type: Optional[BankAccountType] = None
    bankAccountId: Optional[int] = None
    accountCode: Optional[str] = Field(None, pattern=r"^\d{4}(:\d{5})?$")
    reconciledBalance: Optional[int] = None
    reconciledDate: Optional[date] = None  # TODO - new date type


class BankAccountCreateRequest(BankAccountBase, FikenObjectRequest):
    BASE_CLASS: ClassVar[FikenObject] = BankAccount

    _POST_PATH = '/companies/{companySlug}/bankAccounts/'

    @model_validator(mode="after")
    @classmethod
    def validate_foreignService(cls, value):
        if value.type == BankAccountType.FOREIGN:
            if value.foreignService is None:
                raise ValueError("foreignService must be set for foreign bank accounts")
        else:
            if value.foreignService is not None:
                raise ValueError("foreignService is only applicable for foreign bank accounts")

        return value
