import datetime
from typing import Optional

from pydantic import BaseModel, Field

from fiken_py.fiken_object import FikenObjectCounterable, FikenObjectAttachable
from fiken_py.shared_types import Address, InvoiceLine


class Offer(FikenObjectCounterable, FikenObjectAttachable, BaseModel):
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