import datetime
from enum import Enum
from typing import Optional, ClassVar, Any

from pydantic import BaseModel, Field, model_validator

from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import FikenObjectRequest, FikenObject, T, RequestMethod, FikenObjectAttachable
from fiken_py.shared_types import Attachment, AccountingAccount, BankAccountNumber, DraftLine
from fiken_py.models import Contact, Invoice, Offer
from fiken_py.models.credit_note import CreditNote


class DraftType(str, Enum):
    INVOICE = "invoice"
    CASH_INVOICE = "cash_invoice"
    OFFER = "offer"
    CREDIT_NOTE = "credit_note"
    REPEATING_INVOICE = "repeating_invoice"


class DraftBase(BaseModel):
    uuid: Optional[str] = None
    projectId: Optional[int] = None
    lastModifiedDate: Optional[datetime.date] = None
    issueDate: Optional[datetime.date] = None
    invoiceText: Optional[str] = None
    currency: Optional[str] = Field(None, pattern='^[A-Z]{3}$')
    yourReference: Optional[str] = None
    ourReference: Optional[str] = None
    orderReference: Optional[str] = None
    lines: Optional[list[DraftLine]] = []
    net: Optional[int] = None
    gross: Optional[int] = None
    bankAccountNumber: Optional[BankAccountNumber] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    paymentAccount: Optional[AccountingAccount] = None


class Draft(FikenObjectAttachable, DraftBase):
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = None  # Which class to use when making into a real object
    # For example, InvoiceDraft -> Invoice

    draftId: Optional[int] = None
    type: Optional[DraftType] = None
    daysUntilDueDate: Optional[int] = None
    customers: Optional[list[Contact]] = []
    attachments: Optional[list[Attachment]] = []
    createdFromInvoiceId: Optional[int] = None

    def save(self, **kwargs: Any) -> T | None:

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
        dumped = self.model_dump(exclude_unset=True)
        dumped['customerId'] = self.customers[0].contactId
        # TODO - is this really the best way to do this?

        return DraftCreateRequest(**dumped)

    def submit_object(self):
        if self.CREATED_OBJECT_CLASS is None:
            raise NotImplementedError(f"Object {self.__class__.__name__} does not have a TARGET_CLASS specified")

        url = self._get_method_base_URL("CREATE_OBJECT")
        if url is None:
            raise NotImplementedError(f"Object {self.__class__.__name__} does not have a CREATE_OBJECT path specified")

        try:
            response = self._execute_method(RequestMethod.POST, url, draftId=self.draftId)
        except RequestErrorException:
            raise

        loc = response.headers.get('Location')
        if loc is None:
            raise RequestErrorException("No Location header in response")

        return self.CREATED_OBJECT_CLASS._getFromURL(loc)


class DraftCreateRequest(FikenObjectRequest, DraftBase):
    BASE_CLASS: ClassVar[FikenObject] = Draft

    type: DraftType
    daysUntilDueDate: int
    customerId: int

    contactPersonId: Optional[int] = None
    bankAccountNumber: BankAccountNumber  # TODO - maybe optional if set for user?


class InvoiceDraft(Draft):
    _GET_PATH_SINGLE = '/companies/{companySlug}/invoices/drafts/{draftId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/invoices/drafts'
    _DELETE_PATH = '/companies/{companySlug}/invoices/drafts/{draftId}'
    _PUT_PATH = '/companies/{companySlug}/invoices/drafts/{draftId}'

    _CREATE_OBJECT_PATH = '/companies/{companySlug}/invoices/drafts/{draftId}/createInvoice'
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = Invoice

    type: DraftType = DraftType.INVOICE


class InvoiceDraftCreateRequest(DraftCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = InvoiceDraft
    _POST_PATH = '/companies/{companySlug}/invoices/drafts'

    type: DraftType = DraftType.INVOICE


class CreditNoteDraft(Draft):
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = CreditNote

    _GET_PATH_SINGLE = '/companies/{companySlug}/creditNotes/drafts/{draftId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/creditNotes/drafts'
    _DELETE_PATH = '/companies/{companySlug}/creditNotes/drafts/{draftId}'
    _PUT_PATH = '/companies/{companySlug}/creditNotes/drafts/{draftId}'

    _CREATE_OBJECT_PATH = '/companies/{companySlug}/creditNotes/drafts/{draftId}/createCreditNote'

    type: DraftType = DraftType.CREDIT_NOTE


class CreditNoteDraftCreateRequest(DraftCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = CreditNoteDraft
    _POST_PATH = '/companies/{companySlug}/creditNotes/drafts'

    type: DraftType = DraftType.CREDIT_NOTE


class OfferDraft(Draft):
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = Offer

    _GET_PATH_SINGLE = '/companies/{companySlug}/offers/drafts/{draftId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/offers/drafts'
    _DELETE_PATH = '/companies/{companySlug}/offers/drafts/{draftId}'
    _PUT_PATH = '/companies/{companySlug}/offers/drafts/{draftId}'

    _CREATE_OBJECT_PATH = '/companies/{companySlug}/offers/drafts/{draftId}/createOffer'

    type: DraftType = DraftType.OFFER


class OfferDraftCreateRequest(DraftCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = OfferDraft
    _POST_PATH = '/companies/{companySlug}/offers/drafts'

    type: DraftType = DraftType.OFFER
