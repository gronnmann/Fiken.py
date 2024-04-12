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
    streetAddress: Optional[str] = None
    streetAddressLine2: Optional[str] = None
    city: Optional[str] = None
    postCode: Optional[str] = None
    country: str


class AttachmentType(str, Enum):
    INVOICE = 'invoice'
    REMINDER = 'reminder'
    UNSPECIFIED = 'unspecified'
    OCR = 'ocr'
    BANK_STATEMENT = 'bank_statement'


class Attachment(BaseModel):
    identifier: str
    downloadUrl: str
    downloadUrlWithFikenNormalUserCredentials: str
    comment: Optional[str] = None
    type: AttachmentType


class ContactPerson(BaseModel):
    contactPersonId: int # TODO should be maybe none here?
    name: str
    email: str
    phoneNumber: Optional[str] = None
    address: Optional[Address] = None
