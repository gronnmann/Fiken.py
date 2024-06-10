import datetime
import typing
from enum import Enum
from typing import Optional, ClassVar, Any

from pydantic import BaseModel, Field

from fiken_py.authorization import AccessToken
from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import FikenObjectRequest, FikenObject, RequestMethod, FikenObjectAttachable
from fiken_py.shared_types import Attachment, AccountingAccount, BankAccountNumber, DraftLineInvoiceIsh, DraftLineOrder
from fiken_py.models.payment import Payment
from fiken_py.models import Contact, Project


class DraftObject(FikenObjectAttachable):
    """Generic draft object.
    Supports attachments, saving, and submitting to create a real object.

    In practice this class should not be used directly, but rather one of the subclasses.
    """

    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = None  # Which class to use when making into a real object

    @property
    def id_attr(self):
        return "draftId", self.draftId

    def save(self, **kwargs: Any) -> typing.Self | None:

        if self._get_method_base_URL(RequestMethod.PUT) is not None:
            if self.is_new is None:
                raise NotImplementedError(
                    f"Object {self.__class__.__name__} has PUT path specified, but no is_new method")

        if self.is_new:
            return super.save(**kwargs)

        try:
            response = self._execute_method(RequestMethod.PUT, dumped_object=self._to_draft_create_request(),
                                            draftId=self.draftId, **kwargs)
        except RequestErrorException:
            raise

        return self._follow_location_and_update_class(response)

    @property
    def is_new(self):
        return self.draftId is None

    def _to_draft_create_request(self):
        raise NotImplementedError("Method _to_draft_create_request must be implemented in subclass")

    def submit_object(self, companySlug: str = None, token: AccessToken | str = None):
        if self.CREATED_OBJECT_CLASS is None:
            raise NotImplementedError(f"Object {self.__class__.__name__} does not have a TARGET_CLASS specified")

        url = self._get_method_base_URL("CREATE_OBJECT")
        if url is None:
            raise NotImplementedError(f"Object {self.__class__.__name__} does not have a CREATE_OBJECT path specified")

        if token is None:
            token = self._auth_token

        if companySlug is None:
            companySlug = self._company_slug

        try:
            response = self._execute_method(RequestMethod.POST, url, token=token, companySlug=companySlug, draftId=self.draftId)
        except RequestErrorException:
            raise

        loc = response.headers.get('Location')
        if loc is None:
            raise RequestErrorException("No Location header in response")

        return self.CREATED_OBJECT_CLASS._get_from_url(loc, self._auth_token, companySlug=self._company_slug)


class DraftTypeInvoiceIsh(str, Enum):
    INVOICE = "invoice"
    CASH_INVOICE = "cash_invoice"
    OFFER = "offer"
    CREDIT_NOTE = "credit_note"
    ORDER_CONFIRMATION = "order_confirmation"


class DraftInvoiceIshBase(BaseModel):
    uuid: Optional[str] = None
    projectId: Optional[int] = None
    lastModifiedDate: Optional[datetime.date] = None
    issueDate: Optional[datetime.date] = None
    invoiceText: Optional[str] = None
    currency: Optional[str] = Field(None, pattern='^[A-Z]{3}$')
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


class DraftInvoiceIsh(DraftObject, DraftInvoiceIshBase):
    # For example, InvoiceDraft -> Invoice

    draftId: Optional[int] = None
    type: Optional[DraftTypeInvoiceIsh] = None
    daysUntilDueDate: Optional[int] = None
    customers: Optional[list[Contact]] = []
    attachments: Optional[list[Attachment]] = []
    createdFromInvoiceId: Optional[int] = None

    def _to_draft_create_request(self):
        dumped = self.model_dump(exclude_unset=True)
        dumped['customerId'] = self.customers[0].contactId
        # TODO - is this really the best way to do this?

        return DraftInvoiceIshCreateRequest(**dumped)


class DraftInvoiceIshCreateRequest(FikenObjectRequest, DraftInvoiceIshBase):
    BASE_CLASS: ClassVar[FikenObject] = DraftInvoiceIsh

    type: DraftTypeInvoiceIsh
    daysUntilDueDate: int
    customerId: int

    contactPersonId: Optional[int] = None
    bankAccountNumber: BankAccountNumber  # TODO - maybe optional if set for user?


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


class DraftOrder(DraftObject, DraftOrderBase):
    contact: Optional[Contact] = None
    project: Optional[Project] = None

    def _to_draft_create_request(self):
        dumped = self.model_dump(exclude_unset=True)
        dumped['draftId'] = self.draftId

        return DraftOrderCreateRequest(**dumped)


class DraftOrderCreateRequest(FikenObjectRequest, DraftOrderBase):
    BASE_CLASS: ClassVar[FikenObject] = DraftOrder

    cash: bool

    contactId: Optional[int] = None
    projectId: Optional[int] = None


