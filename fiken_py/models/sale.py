import datetime
import typing
from typing import Optional, ClassVar

from pydantic import BaseModel, Field, model_validator

from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import (
    FikenObject,
    FikenObjectAttachable,
    FikenObjectDeleteFlagable,
    RequestMethod,
    FikenObjectPaymentable,
    FikenObjectRequiringRequest,
)
from fiken_py.models.draft import DraftOrder, DraftOrderCreateRequest

from fiken_py.shared_types import OrderLine, Attachment, Note, AccountingAccountAssets
from fiken_py.models.payment import Payment
from fiken_py.shared_enums import SaleKind, VatTypeProductSale
from fiken_py.models import Contact, Project


class Sale(
    FikenObjectRequiringRequest,
    FikenObjectAttachable,
    FikenObjectDeleteFlagable,
    FikenObjectPaymentable,
    BaseModel,
):
    _GET_PATH_SINGLE = "/companies/{companySlug}/sales/{saleId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/sales"
    _DELETE_PATH = "/companies/{companySlug}/sales/{saleId}/delete"
    _SET_SETTLED_PATH = "/companies/{companySlug}/sales/{saleId}/settled"
    _POST_PATH = "/companies/{companySlug}/sales/"
    saleId: Optional[int] = None

    saleNumber: Optional[str] = None
    totalPaid: Optional[int] = None
    totalPaidInCurrency: Optional[int] = None
    dueDate: Optional[datetime.date] = None
    kid: Optional[str] = Field(None, min_length=2, max_length=25)
    paymentAccount: Optional[AccountingAccountAssets] = None
    paymentDate: Optional[datetime.date] = None

    lastModifiedDate: Optional[datetime.date] = None
    transactionId: Optional[int] = None
    date: Optional[datetime.date] = None
    kind: Optional[SaleKind] = None
    netAmount: Optional[int] = None
    vatAmount: Optional[int] = None
    settled: Optional[bool] = None
    settledDate: Optional[datetime.date] = None
    writeOff: Optional[bool] = None
    outstandingBalance: Optional[int] = None
    lines: Optional[list[OrderLine]] = None
    customer: Optional[Contact] = None
    currency: Optional[str] = Field(pattern=r"^[A-Z]{3}$")
    salePayments: Optional[list[Payment]] = []
    saleAttachments: Optional[list[Attachment]] = []
    project: Optional[Project] = None
    notes: Optional[list[Note]] = None
    deleted: Optional[bool] = None

    @property
    def id_attr(self):
        return "saleId", self.saleId

    def set_settled(self, settledDate: datetime.date = datetime.date.today()) -> None:
        """Sets the sale as settled with the given date (equivalent to 'Sett til oppgjort uten betaling')."""
        url = self._get_method_base_URL("SET_SETTLED")

        try:
            response = self._execute_method(
                RequestMethod.PATCH,
                url=url,
                saleId=self.saleId,
                settledDate=settledDate,
            )
        except RequestErrorException:
            raise
        if response.status_code != 200:
            raise RequestErrorException(
                f"Failed to set sale as settled. Response: {response.status_code} {response.text}"
            )

        self._refresh_object()

    def _to_request_object(
        self, paymentFee: Optional[int] = None, **kwargs
    ) -> BaseModel:
        return SaleRequest(
            customerId=self.customer.contactId if self.customer is not None else None,
            projectId=self.project.projectId if self.project is not None else None,
            paymentFee=paymentFee,
            **FikenObjectRequiringRequest._pack_common_fields(self, SaleRequest),
        )


class SaleRequest(BaseModel):
    date: datetime.date
    kind: SaleKind
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    lines: list[OrderLine]

    customerId: Optional[int] = None
    paymentFee: Optional[int] = None
    projectId: Optional[int] = None
    saleNumber: Optional[str] = None
    totalPaid: Optional[int] = None
    totalPaidInCurrency: Optional[int] = None
    dueDate: Optional[datetime.date] = None
    kid: Optional[str] = Field(None, min_length=2, max_length=25)
    paymentAccount: Optional[AccountingAccountAssets] = None
    paymentDate: Optional[datetime.date] = None

    @model_validator(mode="after")
    @classmethod
    def validate_not_invoice(cls, value):
        assert (
            value.kind is not SaleKind.INVOICE
        ), "SaleType INVOICE is not allowed for SaleRequest. Please use 'Invoice' instead"
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_if_customerid_should_exist(cls, value):
        if value.kind == SaleKind.CASH_SALE:
            assert (
                value.customerId is None
            ), "customerId cannot be provided for cash sales"

        elif value.kind == SaleKind.EXTERNAL_INVOICE:
            assert (
                value.customerId is not None
            ), "customerId must be provided for external invoices"
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_date_if_cashsale(cls, value):
        if value.kind == SaleKind.CASH_SALE:
            assert (
                value.paymentDate is not None
            ), "paymentDate must be provided for cash sales"
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_payment_account_if_payment_date(cls, value):
        if value.paymentDate is not None:
            assert (
                value.paymentAccount is not None
            ), "paymentAccount must be provided if paymentDate is provided"
        return value


class SaleDraft(DraftOrder):
    _GET_PATH_SINGLE = "/companies/{companySlug}/sales/drafts/{draftId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/sales/drafts"
    _DELETE_PATH = "/companies/{companySlug}/sales/drafts/{draftId}"
    _PUT_PATH = "/companies/{companySlug}/sales/drafts/{draftId}"
    _POST_PATH = "/companies/{companySlug}/sales/drafts"

    _CREATE_OBJECT_PATH = "/companies/{companySlug}/sales/drafts/{draftId}/createSale"
    CREATED_OBJECT_CLASS: ClassVar[typing.Type[FikenObject]] = Sale

    def _to_request_object(self, **kwargs) -> BaseModel:
        return SaleDraftRequest(
            projectId=self.project.projectId if self.project is not None else None,
            contactId=self.contact.contactId if self.contact is not None else None,
            **FikenObjectRequiringRequest._pack_common_fields(
                self, DraftOrderCreateRequest
            ),
        )


class SaleDraftRequest(DraftOrderCreateRequest):
    @model_validator(mode="after")
    @classmethod
    def correct_vat_type(cls, value):
        for line in value.lines:
            try:
                VatTypeProductSale(line.vatType)
                return value
            except ValueError:
                raise ValueError(
                    "Only VatTypeProductPurchase is allowed for sale drafts"
                )
