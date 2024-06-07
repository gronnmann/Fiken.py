from __future__ import annotations

from datetime import date
from typing import Optional, Annotated, ClassVar

from pydantic import BaseModel, Field, model_validator


from fiken_py.shared_enums import AttachmentType, VatTypeProductSale, VatTypeProductPurchase
from fiken_py.vat_validation import VATValidator

AccountingAccount = Annotated[str, Field(pattern=r"^[1-8]\d{3}(:\d{5})?$")]  # All kontoklasser

AccountingAccountAssets = Annotated[str, Field(pattern=r"^1\d{3}(:\d{5})?$")]  # Kontoklasse 1
AccountingAccountEquityAndLiabilities = Annotated[str, Field(pattern=r"^2\d{3}(:\d{5})?$")]  # Kontoklasse 2

AccountingAccountIncome = Annotated[str, Field(pattern=r"^[3|8]\d{3}$")]  # Kontoklasse 3
AccountingAccountCosts = Annotated[str, Field(pattern=r"^[4-8]\d{3}$")]  # Kontoklasse 4-7

BankAccountNumber = Annotated[str, Field(pattern=r"^\d{11}$")]


class Address(BaseModel):
    streetAddress: Optional[str] = None
    streetAddressLine2: Optional[str] = None
    city: Optional[str] = None
    postCode: Optional[str] = None
    country: str


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
    account: Optional[AccountingAccount] = None
    vatCode: Optional[str] = None
    debitAccount: Optional[str] = None  # TODO - update with account type
    debitVatCode: Optional[int] = None  # TODO - code the vat codes?
    creditAccount: Optional[str] = None  # TODO - update with account type
    creditVatCode: Optional[int] = None  # TODO - code the vat codes?
    projectId: Optional[list] = None  # TODO - find out what list this is
    lastModifiedDate: Optional[date] = None


class Note(BaseModel):
    description: Optional[str] = None
    author: Optional[str] = None
    note: Optional[str] = None


class OrderLine(BaseModel):
    description: Optional[str] = None
    netPrice: Optional[int] = None
    vat: Optional[int] = None
    account: Optional[AccountingAccount] = None
    vatType: VatTypeProductSale | VatTypeProductPurchase
    netPriceInCurrency: Optional[int] = None
    vatInCurrency: Optional[int] = None
    projectId: Optional[int] = None

    @model_validator(mode="after")
    @classmethod
    def validate_netPrice_or_netPriceInCurrency(cls, value):
        assert (value.netPrice is not None) or (value.netPriceInCurrency is not None), \
            "Either netPrice or netPriceInCurrency must be provided"
        return value


class InvoiceIshLineBase(BaseModel):
    validate_product_or_line: ClassVar[bool] = False

    incomeAccount: Optional[AccountingAccountIncome] = None
    vatType: Optional[VatTypeProductSale] = None
    unitPrice: Optional[int] = None
    quantity: Optional[int] = None
    discount: Optional[int] = None
    productId: Optional[int] = None
    description: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, max_length=200)

    @model_validator(mode="after")
    @classmethod
    def provided_prod_or_line_data(cls, value):
        if not value.validate_product_or_line:
            return value  # Only validate requests

        product_provided = value.productId is not None
        line_provided = ((value.unitPrice is not None) and (value.vatType is not None) and
                         (value.description is not None) and (value.incomeAccount is not None))

        assert product_provided or line_provided, "Either productId or unitPRice, description, vatType and incomeAccount must be provided"

        return value

    @model_validator(mode="after")
    def validate_vat(cls, value):
        vat: VatTypeProductSale = value.vatType
        incomeAccount: AccountingAccount = value.incomeAccount

        if incomeAccount is not None:
            assert VATValidator.validate_vat_type_sale(vat, incomeAccount), "Vat type is not valid for income account"

        return value  # TODO - own validation class


class CreditNotePartialRequestLine(InvoiceIshLineBase):
    validate_product_or_line: ClassVar[bool] = True

    quantity: int


class DraftLineInvoiceIsh(InvoiceIshLineBase):
    validate_product_or_line: ClassVar[bool] = True

    invoiceishDraftLineId: Optional[int] = None
    lastModifiedDate: Optional[date] = None


class InvoiceLineBase(InvoiceIshLineBase):
    net: Optional[int] = None
    vat: Optional[int] = None
    gross: Optional[int] = None
    vatInPercent: Optional[float] = None
    unitPrice: Optional[int] = None
    productName: Optional[str] = None


class InvoiceLineRequest(InvoiceLineBase):
    validate_product_or_line: ClassVar[bool] = True

    quantity: int


class InvoiceLine(InvoiceLineBase):
    netInNok: Optional[int] = None
    vatInNok: Optional[int] = None
    grossInNok: Optional[int] = None
    quantity: Optional[int] = None


class DraftLineOrderBase(BaseModel):
    text: Optional[str] = None
    vatType: Optional[VatTypeProductSale | VatTypeProductPurchase] = None
    incomeAccount: Optional[AccountingAccountIncome | AccountingAccountCosts] = None
    net: Optional[int] = None
    gross: Optional[int] = None


class DraftLineOrder(DraftLineOrderBase):
    project: Optional['Project'] = None


class DraftLineOrderRequest(DraftLineOrderBase):
    projectId: Optional[int] = None


class Counter(BaseModel):
    value: int
