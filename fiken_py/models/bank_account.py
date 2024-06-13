from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator

from fiken_py.fiken_object import FikenObjectRequiringRequest
from fiken_py.shared_types import (
    AccountingAccountAssets,
    BankAccountNumber,
)


class BankAccountType(str, Enum):
    NORMAL = "normal"
    TAX_DEDUCTION = "tax_deduction"
    FOREIGN = "foreign"
    CREDIT_CARD = "credit_card"


class BankAccount(BaseModel, FikenObjectRequiringRequest):
    _GET_PATH_SINGLE = "/companies/{companySlug}/bankAccounts/{bankAccountId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/bankAccounts/"
    _POST_PATH = "/companies/{companySlug}/bankAccounts/"

    name: Optional[str] = None
    bankAccountNumber: Optional[BankAccountNumber] = None
    type: Optional[BankAccountType] = None
    bankAccountId: Optional[int] = None
    accountCode: Optional[AccountingAccountAssets] = None
    reconciledBalance: Optional[int] = None
    reconciledDate: Optional[date] = None
    bic: Optional[str] = None
    iban: Optional[str] = None
    foreignService: Optional[str] = None
    inactive: Optional[bool] = False

    @property
    def id_attr(self):
        return "bankAccountId", self.bankAccountId

    def _to_request_object(self, **kwargs) -> BaseModel:
        return BankAccountRequest(
            **FikenObjectRequiringRequest._pack_common_fields(self, BankAccountRequest)
        )


class BankAccountRequest(BaseModel):
    name: str
    bankAccountNumber: BankAccountNumber
    bic: Optional[str] = None
    iban: Optional[str] = None
    foreignService: Optional[str] = None
    type: BankAccountType
    inactive: bool = False

    @model_validator(mode="after")
    @classmethod
    def validate_foreignService(cls, value):
        if value.type == BankAccountType.FOREIGN:
            if value.foreignService is None:
                raise ValueError("foreignService must be set for foreign bank accounts")
        else:
            if value.foreignService is not None:
                raise ValueError(
                    "foreignService is only applicable for foreign bank accounts"
                )

        return value
