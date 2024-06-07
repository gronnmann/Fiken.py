import datetime
from typing import Optional, ClassVar

from pydantic import BaseModel, Field

from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import FikenObjectAttachable, FikenObjectCountable, RequestMethod, FikenObject
from fiken_py.models import InvoiceDraft
from fiken_py.models.draft import DraftInvoiceIsh, DraftInvoiceIshCreateRequest, DraftTypeInvoiceIsh
from fiken_py.shared_types import InvoiceLine, Address
import test_online.shared_tests as shared_tests


class OrderConfirmation(FikenObjectCountable, FikenObjectAttachable, BaseModel):
    _GET_PATH_SINGLE = '/companies/{companySlug}/orderConfirmations/{confirmationId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/orderConfirmations/'

    _COUNTER_PATH = '/companies/{companySlug}/orderConfirmations/counter'
    _TO_INVOICE_PATH = '/companies/{companySlug}/orderConfirmations/{confirmationId}/createInvoiceDraft'

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
    currency: Optional[str] = Field(None, pattern='^[A-Z]{3}$')
    contactId: Optional[int] = None
    contactPersonId: Optional[int] = None
    projectId: Optional[int] = None
    createdInvoice: Optional[int] = None
    archived: Optional[bool] = None
    internalComment: Optional[str] = None

    @classmethod
    def to_invoice_draft_cls(cls, **kwargs) -> InvoiceDraft:
        url = cls._get_method_base_URL("TO_INVOICE")

        try:
            response = cls._execute_method(RequestMethod.POST, url, **kwargs)
        except RequestErrorException as e:
            raise e

        return InvoiceDraft._getFromURL(response.headers['Location'])

    def to_invoice_draft(self, **kwargs) -> InvoiceDraft:
        return self.to_invoice_draft_cls(confirmationId=self.confirmationId, **kwargs)


class OrderConfirmationDraft(DraftInvoiceIsh):
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = OrderConfirmation

    _GET_PATH_SINGLE = '/companies/{companySlug}/orderConfirmations/drafts/{draftId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/orderConfirmations/drafts'
    _DELETE_PATH = '/companies/{companySlug}/orderConfirmations/drafts/{draftId}'
    _PUT_PATH = '/companies/{companySlug}/orderConfirmations/drafts/{draftId}'

    _CREATE_OBJECT_PATH = '/companies/{companySlug}/orderConfirmations/drafts/{draftId}/createOrderConfirmation'


class OrderConfirmationDraftCreateRequest(DraftInvoiceIshCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = OrderConfirmationDraft
    _POST_PATH = '/companies/{companySlug}/orderConfirmations/drafts'

    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.ORDER_CONFIRMATION
