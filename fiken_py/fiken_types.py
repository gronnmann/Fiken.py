from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class CaseInsensitiveEnum(str, Enum):
    """Enum that matches values case-insensitively.
    Used in places API returns values non-consistently."""
    @classmethod
    def _missing_(cls, value: str):
        for member in cls:
            if member.upper() == value.upper():
                return member
        return None


class CompanyVatType(str, Enum):
    NO = 'no'
    YEARLY = 'yearly'
    MONTHLY = 'monthly'
    BI_MONTHLY = 'bi-monthly'


class ProductVatType(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'

    # Sales
    EXEMPT_IMPORT_EXPORT = 'EXEMPT_IMPORT_EXPORT'
    EXEMPT = 'EXEMPT'
    OUTSIDE = 'OUTSIDE'
    EXEMPT_REVERSE = 'EXEMPT_REVERSE'

    # Purcase
    HIGH_DIRECT = 'HIGH_DIRECT'
    HIGH_BASIS = 'HIGH_BASIS'
    MEDIUM_DIRECT = 'MEDIUM_DIRECT'
    MEDIUM_BASIS = 'MEDIUM_BASIS'
    NONE_IMPORT_BASIS = 'NONE_IMPORT_BASIS'
    HIGH_FOREIGN_SERVICE_DEDUCTIBLE = 'HIGH_FOREIGN_SERVICE_DEDUCTIBLE'
    HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE = 'HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE'
    LOW_FOREIGN_SERVICE_DEDUCTIBLE = 'LOW_FOREIGN_SERVICE_DEDUCTIBLE'
    LOW_FOREIGN_SERVICE_NONDEDUCTIBLE = 'LOW_FOREIGN_SERVICE_NONDEDUCTIBLE'
    HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE = 'HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE'
    HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE = 'HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE'


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


class ProductSalesLine(BaseModel):
    count: Optional[int] = None
    sales: Optional[int] = None
    netAmount: Optional[int] = None
    vatAmount: Optional[int] = None
    grossAmount: Optional[int] = None


class JournalEntryLine(BaseModel):
    amount: int
    account: Optional[str] = None  # TODO - update with account type
    vatCode: Optional[str] = None
    debitAccount: Optional[str] = None  # TODO - update with account type
    debitVatCode: Optional[int] = None  # TODO - code the vat codes?
    creditAccount: Optional[str] = None  # TODO - update with account type
    creditVatCode: Optional[int] = None  # TODO - code the vat codes?
    projectId: Optional[list] = None  # TODO - find out what list this is
    lastModifiedDate: Optional[date] = None
