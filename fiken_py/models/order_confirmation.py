import datetime
import typing
from typing import Optional, ClassVar

from pydantic import BaseModel, Field

from fiken_py.authorization import AccessToken
from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import (
    FikenObjectAttachable,
    FikenObjectCountable,
    RequestMethod,
    FikenObject,
    OptionalAccessToken,
    FikenObjectRequiringRequest,
)
from fiken_py.models import InvoiceDraft
from fiken_py.models.draft import (
    DraftInvoiceIsh,
    DraftInvoiceIshRequest,
    DraftTypeInvoiceIsh,
)
from fiken_py.shared_types import InvoiceLine, Address


class OrderConfirmation(FikenObjectCountable, FikenObjectAttachable, BaseModel):
    _GET_PATH_SINGLE = "/companies/{companySlug}/orderConfirmations/{confirmationId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/orderConfirmations/"

    _COUNTER_PATH = "/companies/{companySlug}/orderConfirmations/counter"
    _TO_INVOICE_PATH = "/companies/{companySlug}/orderConfirmations/{confirmationId}/createInvoiceDraft"

    confirmationId: Optional[int] = None
    confirmationDraftUuid: Optional[str] = None
    date: Optional[datetime.date] = None
    confirmationNumber: Optional[int] = None
    net: Optional[int] = None
    vat: Optional[int] = None
    gross: Optional[int] = None
    comment: Optional[str] = None
    yourReference: Optional[str] = None
    ourReference: Optional[str] = None
    discount: Optional[int] = None
    address: Optional[Address] = None
    lines: Optional[list[InvoiceLine]] = []
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    contactId: Optional[int] = None
    contactPersonId: Optional[int] = None
    projectId: Optional[int] = None
    createdInvoice: Optional[int] = None
    archived: Optional[bool] = None
    internalComment: Optional[str] = None

    @property
    def id_attr(self):
        return "confirmationId", self.confirmationId

    @classmethod
    def to_invoice_draft_cls(
        cls, token: OptionalAccessToken = None, **kwargs
    ) -> InvoiceDraft:
        url = cls._get_method_base_URL("TO_INVOICE")

        try:
            response = cls._execute_method(RequestMethod.POST, url, **kwargs)
        except RequestErrorException as e:
            raise e

        return InvoiceDraft._get_from_url(response.headers["Location"], token, **kwargs)

    def to_invoice_draft(self, **kwargs) -> InvoiceDraft:
        return self.to_invoice_draft_cls(confirmationId=self.confirmationId, **kwargs)


class OrderConfirmationDraft(DraftInvoiceIsh):
    CREATED_OBJECT_CLASS: ClassVar[typing.Type[FikenObject]] = OrderConfirmation

    _GET_PATH_SINGLE = "/companies/{companySlug}/orderConfirmations/drafts/{draftId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/orderConfirmations/drafts"
    _DELETE_PATH = "/companies/{companySlug}/orderConfirmations/drafts/{draftId}"
    _PUT_PATH = "/companies/{companySlug}/orderConfirmations/drafts/{draftId}"
    _POST_PATH = "/companies/{companySlug}/orderConfirmations/drafts"

    _CREATE_OBJECT_PATH = "/companies/{companySlug}/orderConfirmations/drafts/{draftId}/createOrderConfirmation"

    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.ORDER_CONFIRMATION

    def _to_request_object(
        self,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs
    ) -> BaseModel:
        if contactId is None:
            if self.customers is not None and len(self.customers) > 0:
                contactId = self.customers[0].contactId

        if contactPersonId is None:
            if self.customers is not None and len(self.customers) > 0:
                if (
                    self.customers[0] is not None
                    and len(self.customers[0].contactPerson) > 0
                ):
                    contactPersonId = self.customers[0].contactPerson[0].contactPersonId

        return OrderConfirmationDraftRequest(
            customerId=contactId,
            contactPersonId=contactPersonId,
            **FikenObjectRequiringRequest._pack_common_fields(
                self, OrderConfirmationDraftRequest
            )
        )


class OrderConfirmationDraftRequest(DraftInvoiceIshRequest):
    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.ORDER_CONFIRMATION
