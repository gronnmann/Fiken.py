import datetime
from typing import Optional, ClassVar

from pydantic import BaseModel, Field

from fiken_py.fiken_object import FikenObjectCountable, FikenObjectAttachable, FikenObject
from fiken_py.models.draft import DraftInvoiceIsh, DraftTypeInvoiceIsh, DraftInvoiceIshCreateRequest
from fiken_py.shared_types import Address, InvoiceLine


class Offer(FikenObjectCountable, FikenObjectAttachable, BaseModel):
    _GET_PATH_SINGLE = '/companies/{companySlug}/offers/{offerId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/offers/'

    _COUNTER_PATH = '/companies/{companySlug}/offers/counter'

    offerId: Optional[int] = None
    offerDraftUuid: Optional[str] = None
    date: Optional[datetime.date] = None
    offerNumber: Optional[int] = None
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
    archived: Optional[bool] = None

    @property
    def id_attr(self):
        return "offerId", self.offerId


class OfferDraft(DraftInvoiceIsh):
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = Offer

    _GET_PATH_SINGLE = '/companies/{companySlug}/offers/drafts/{draftId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/offers/drafts'
    _DELETE_PATH = '/companies/{companySlug}/offers/drafts/{draftId}'
    _PUT_PATH = '/companies/{companySlug}/offers/drafts/{draftId}'

    _CREATE_OBJECT_PATH = '/companies/{companySlug}/offers/drafts/{draftId}/createOffer'

    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.OFFER


class OfferDraftCreateRequest(DraftInvoiceIshCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = OfferDraft
    _POST_PATH = '/companies/{companySlug}/offers/drafts'

    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.OFFER
