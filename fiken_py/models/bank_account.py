from typing import Optional

from pydantic import BaseModel, model_validator

from fiken_py.fiken_object import FikenObject, T
from fiken_py.fiken_types import BankAccountType


class BankAccount(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/bankAccounts/{bankAccountId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/bankAccounts/'

    bankAccountId: int = None
    name: str
    accountCode: str = None
    bankAccountNumber: str  # TODO - class
    iban: Optional[str] = None
    bic: Optional[str] = None
    foreignService: Optional[str] = None
    type: BankAccountType
    reconciledBalance: int = None
    reconciledDate: Optional[str] = None  # TODO - new date type
    inactive: bool = False

    # TODO - validate foreign

    # @model_validator(mode='after')
    # def check_foreign_service(cls, values):
    #     if values.get('type') == BankAccountType.FOREIGN and not values.get('foreignService'):
    #         raise ValueError('foreignService must be provided for foreign bank accounts')

    def _to_create_request(self):
        return BankAccountCreateRequest(
            name=self.name,
            bankAccountNumber=self.bankAccountNumber,
            bic=self.bic,
            iban=self.iban,
            foreignService=self.foreignService,
            type=self.type,
            inactive=self.inactive
        )

    def save(self, **kwargs):
        # Override with the create request type
        # TODO - override self with the new object
        self = self._to_create_request().save(**kwargs)


class BankAccountCreateRequest(BaseModel, FikenObject):
    _POST_PATH = '/companies/{companySlug}/bankAccounts/'

    name: str
    bankAccountNumber: str
    bic: Optional[str] = None,
    iban: Optional[str] = None,
    foreignService: Optional[str] = None,
    type: BankAccountType
    inactive: bool = False

    @classmethod
    def getFromURL(cls, url: str) -> T:
        # Redirect to the normal BankAccount
        return BankAccount.getFromURL(url)
