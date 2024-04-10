from enum import Enum
from typing import Optional

from pydantic import BaseModel


class VatType(str, Enum):
    NO = 'no'
    YEARLY = 'yearly'
    MONTHLY = 'monthly'
    BI_MONTHLY = 'bi-monthly'

class BankAccountType(str, Enum):
    NORMAL = 'normal'
    TAX_DEDUCTION = 'tax_deduction'
    FOREIGN = 'foreign'
    CREDIT_CARD = 'credit_card'

class Address(BaseModel):
    streetAddress: str
    streetAddressLine2: Optional[str] = None
    city: str
    postCode: str
    country: str

