import abc
import datetime
import typing
from abc import ABC
from enum import Enum
from typing import Optional, ClassVar, Any

from pydantic import BaseModel, Field

from fiken_py.authorization import AccessToken
from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import (
    FikenObject,
    RequestMethod,
    FikenObjectAttachable,
    OptionalAccessToken,
    FikenObjectRequiringRequest,
)
from fiken_py.shared_types import (
    Attachment,
    AccountingAccount,
    BankAccountNumber,
    DraftLineInvoiceIsh,
    DraftLineOrder,
)
from fiken_py.models.payment import Payment
from fiken_py.models import Contact, Project


class DraftObject(FikenObjectAttachable, FikenObjectRequiringRequest, ABC):
    """Generic draft object.
    Supports attachments, saving, and submitting to create a real object.

    In practice this class should not be used directly, but rather one of the subclasses.
    """

    CREATED_OBJECT_CLASS: ClassVar[typing.Type[FikenObject]]

    @property
    def id_attr(self):
        return "draftId", self.draftId

    def save(self, token: OptionalAccessToken = None, **kwargs: Any) -> typing.Self:

        return super().save(token=token, draftId=self.draftId, **kwargs)

    def submit_object(
        self, companySlug: Optional[str] = None, token: OptionalAccessToken = None
    ):
        if self.CREATED_OBJECT_CLASS is None:
            raise NotImplementedError(
                f"Object {self.__class__.__name__} does not have a TARGET_CLASS specified"
            )

        url = self._get_method_base_URL("CREATE_OBJECT")
        if url is None:
            raise NotImplementedError(
                f"Object {self.__class__.__name__} does not have a CREATE_OBJECT path specified"
            )

        if token is None:
            token = self._auth_token

        if companySlug is None:
            companySlug = self._company_slug

        try:
            response = self._execute_method(
                RequestMethod.POST,
                url,
                token=token,
                companySlug=companySlug,
                draftId=self.draftId,
            )
        except RequestErrorException:
            raise

        loc = response.headers.get("Location")
        if loc is None:
            raise RequestErrorException("No Location header in response")

        return self.CREATED_OBJECT_CLASS._get_from_url(
            loc, self._auth_token, companySlug=self._company_slug
        )


class DraftTypeInvoiceIsh(str, Enum):
    INVOICE = "invoice"
    CASH_INVOICE = "cash_invoice"
    OFFER = "offer"
    CREDIT_NOTE = "credit_note"
    ORDER_CONFIRMATION = "order_confirmation"


class DraftInvoiceIsh(DraftObject, BaseModel, ABC):
    # For example, InvoiceDraft -> Invoice
    uuid: Optional[str] = None
    projectId: Optional[int] = None
    lastModifiedDate: Optional[datetime.date] = None
    issueDate: Optional[datetime.date] = None
    invoiceText: Optional[str] = None
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    yourReference: Optional[str] = None
    ourReference: Optional[str] = None
    orderReference: Optional[str] = None
    lines: Optional[list[DraftLineInvoiceIsh]] = []
    net: Optional[int] = None
    gross: Optional[int] = None
    bankAccountNumber: Optional[BankAccountNumber] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    paymentAccount: Optional[AccountingAccount] = None
    draftId: Optional[int] = None
    type: Optional[DraftTypeInvoiceIsh] = None
    daysUntilDueDate: Optional[int] = None
    customers: Optional[list[Contact]] = []
    attachments: Optional[list[Attachment]] = []
    createdFromInvoiceId: Optional[int] = None


class DraftInvoiceIshRequest(BaseModel):
    type: DraftTypeInvoiceIsh
    daysUntilDueDate: int
    customerId: int
    bankAccountNumber: BankAccountNumber

    contactPersonId: Optional[int] = None
    uuid: Optional[str] = None
    projectId: Optional[int] = None
    lastModifiedDate: Optional[datetime.date] = None
    issueDate: Optional[datetime.date] = None
    invoiceText: Optional[str] = None
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    yourReference: Optional[str] = None
    ourReference: Optional[str] = None
    orderReference: Optional[str] = None
    lines: Optional[list[DraftLineInvoiceIsh]] = []
    net: Optional[int] = None
    gross: Optional[int] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    paymentAccount: Optional[AccountingAccount] = None


class DraftOrderBase(BaseModel):
    draftId: Optional[int] = None
    uuid: Optional[str] = None
    invoiceIssueDate: Optional[datetime.date] = None
    dueDate: Optional[datetime.date] = None
    invoiceNumber: Optional[str] = None
    cash: Optional[bool] = None
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    kid: Optional[str] = None
    paid: Optional[bool] = None
    attachments: Optional[list[Attachment]] = []
    payments: Optional[list[Payment]] = []
    lines: Optional[list[DraftLineOrder]] = []


class DraftOrder(DraftObject, DraftOrderBase, ABC):
    contact: Optional[Contact] = None
    project: Optional[Project] = None

    def _to_draft_create_request(self):
        dumped = self.model_dump(exclude_unset=True)
        dumped["draftId"] = self.draftId

        return DraftOrderCreateRequest(**dumped)


class DraftOrderCreateRequest(DraftOrderBase):
    cash: bool

    contactId: Optional[int] = None
    projectId: Optional[int] = None
