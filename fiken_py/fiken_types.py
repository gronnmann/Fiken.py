from datetime import date
from enum import Enum
from typing import Optional, Union, Annotated

from pydantic import BaseModel, field_validator, Field, model_validator

AccountCode = Annotated[str, Field(pattern=r"^\d{4}(:\d{5})?$")]


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


class VatTypeProduct(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'


class VatTypeProductSale(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'

    EXEMPT_IMPORT_EXPORT = 'EXEMPT_IMPORT_EXPORT'
    EXEMPT = 'EXEMPT'
    OUTSIDE = 'OUTSIDE'
    EXEMPT_REVERSE = 'EXEMPT_REVERSE'


class VatTypeProductPurcase(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'

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
    identifier: Optional[str] = None
    downloadUrl: Optional[str] = None
    downloadUrlWithFikenNormalUserCredentials: Optional[str] = None
    comment: Optional[str] = None
    type: Optional[AttachmentType] = None


class ProductSalesLine(BaseModel):
    count: Optional[int] = None
    sales: Optional[int] = None
    netAmount: Optional[int] = None
    vatAmount: Optional[int] = None
    grossAmount: Optional[int] = None


class JournalEntryLine(BaseModel):
    amount: int
    account: Optional[AccountCode] = None
    vatCode: Optional[str] = None
    debitAccount: Optional[str] = None  # TODO - update with account type
    debitVatCode: Optional[int] = None  # TODO - code the vat codes?
    creditAccount: Optional[str] = None  # TODO - update with account type
    creditVatCode: Optional[int] = None  # TODO - code the vat codes?
    projectId: Optional[list] = None  # TODO - find out what list this is
    lastModifiedDate: Optional[date] = None


class Payment(BaseModel):
    description: Optional[str] = None
    paymentId: Optional[int] = None
    date: date
    account: str  # TODO - update with account type
    amount: int
    amountInNok: Optional[int] = None
    currency: Optional[str] = None
    fee: Optional[int] = None


class SaleKind(str, Enum):
    CASH_SALE = 'cash_sale'
    INVOICE = 'invoice'
    EXTERNAL_INVOICE = 'external_invoice'


class OrderLine(BaseModel):
    description: Optional[str] = None
    netPrice: Optional[int] = None
    vat: Optional[int] = None
    account: Optional[Union[str, int]] = None  # TODO - update with account type
    vatType: VatTypeProductSale
    netPriceInCurrency: Optional[int] = None
    vatInCurrency: Optional[int] = None
    projectId: Optional[int] = None


class Note(BaseModel):
    description: Optional[str] = None
    author: Optional[str] = None
    note: Optional[str] = None


class InvoiceLineBase(BaseModel):
    net: Optional[int] = None
    vat: Optional[int] = None
    vatType: Optional[VatTypeProduct] = None
    gross: Optional[int] = None
    vatInPercent: Optional[int] = None
    unitPrice: Optional[int] = None
    discount: Optional[int] = None
    productId: Optional[int] = None
    productName: Optional[str] = None
    description: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, max_length=200)
    incomeAccount: Optional[Union[str | int]] = None


class InvoiceLineRequest(InvoiceLineBase):
    # TODO - validate - either product line, OR text line WITH price AND vat
    quantity: int

    # TODO - only allow productName when productId not provided
    # TODO - if no product id, force incomeAccount

    @model_validator(mode="after")
    @classmethod
    def provided_prod_or_line_data(cls, value):
        product_provided = value.productId is not None
        line_provided = ((value.unitPrice is not None) and (value.vatType is not None) and
                         (value.description is not None) and (value.incomeAccount is not None))

        assert product_provided or line_provided, "Either productId or unitPRice, description, vatType and incomeAccount must be provided"

        return value


class InvoiceLine(InvoiceLineBase):
    netInNok: Optional[int] = None
    vatInNok: Optional[int] = None
    grossInNok: Optional[int] = None
    quantity: Optional[int] = None


class SendInvoiceMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    EHF = "ehf"
    EFAKTURA = "efaktura"
    LETTER = "letter"
    AUTO = "auto"


class SendInvoiceEmailOption(str, Enum):
    DOCUMENT_LINK = "document_link"
    ATTACHMENT = "attachment"
    AUTO = "auto"


class DraftType(str, Enum):
    INVOICE = "invoice"
    CASH_INVOICE = "cash_invoice"
    OFFER = "offer"
    CREDIT_NOTE = "credit_note"
    REPEATING_INVOICE = "repeating_invoice"


class DraftLine(BaseModel):
    quantity: int

    invoiceishDraftLineId: Optional[int] = None
    lastModifiedDate: Optional[date] = None
    productId: Optional[int] = None
    description: Optional[str] = None
    unitPrice: Optional[int] = None
    vatType: Optional[VatTypeProductSale] = None
    discount: Optional[int] = None
    comment: Optional[str] = None
    incomeAccount: Optional[str] = None
