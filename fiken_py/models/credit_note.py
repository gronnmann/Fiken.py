from __future__ import annotations

import datetime
from typing import Optional, TypeVar

from pydantic import BaseModel, Field

from fiken_py.errors import RequestContentNotFoundException, RequestErrorException
from fiken_py.fiken_object import FikenObjectAttachable, RequestMethod, FikenObjectCounterable
from fiken_py.shared_types import Address, InvoiceLine, Attachment, CreditNotePartialRequestLine
from fiken_py.models import Contact, Project, Sale, Invoice

CN = TypeVar('CN', bound='CreditNote')


class FullCreditNoteRequest(BaseModel):
    issueDate: datetime.date
    invoiceId: int

    creditNoteText: Optional[str] = None


class PartialCreditNoteRequest(BaseModel):
    issueDate: datetime.date

    ourReference: Optional[str] = None
    yourReference: Optional[str] = None
    project: Optional[int] = None
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    invoiceId: Optional[int] = None
    contactId: Optional[int] = None
    contactPersonId: Optional[int] = None
    creditNoteText: Optional[str] = None
    lines: list[CreditNotePartialRequestLine]


class CreditNote(FikenObjectCounterable, FikenObjectAttachable, BaseModel):
    _GET_PATH_SINGLE = '/companies/{companySlug}/creditNotes/{creditNoteId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/creditNotes/'

    _POST_FULL_PATH = '/companies/{companySlug}/creditNotes/full'
    _POST_PARTIAL_PATH = '/companies/{companySlug}/creditNotes/partial'

    _COUNTER_PATH = '/companies/{companySlug}/creditNotes/counter'

    creditNoteId: int
    creditNoteNumber: int
    net: int
    vat: int
    gross: int
    netInNok: int
    vatInNok: int
    grossInNok: int
    address: Address

    creditNoteText: Optional[str] = None
    settled: Optional[bool] = None
    associatedInvoiceId: Optional[int] = None
    creditNoteDraftUuid: Optional[str] = None
    creditNotePdf: Optional[Attachment] = None
    project: Optional[Project] = None
    sale: Optional[Sale] = None

    kid: Optional[str] = None
    customer: Optional[Contact] = None
    yourReference: Optional[str] = None
    ourReference: Optional[str] = None
    orderReference: Optional[str] = None
    lines: Optional[list[InvoiceLine]] = []
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    issueDate: Optional[datetime.date] = None

    @classmethod
    def create_from_invoice_full(cls, invoiceId: int, issueDate: datetime.date | str = None,
                                 creditNoteText: str = None, companySlug: str = None) -> CN:

        try:
            invoice = Invoice.get(invoiceId=invoiceId, companySlug=companySlug)
        except RequestErrorException:
            raise

        if invoice is None:
            raise RequestContentNotFoundException(f"Invoice with id {invoiceId} not found.")

        credit_note_request = FullCreditNoteRequest(
            issueDate=issueDate if issueDate is not None else datetime.date.today(),
            invoiceId=invoiceId,
            creditNoteText=creditNoteText
        )

        try:
            response = cls._execute_method(RequestMethod.POST, url=cls._get_method_base_URL("POST_FULL"),
                                           dumped_object=credit_note_request, companySlug=companySlug)
        except RequestErrorException:
            raise

        loc = response.headers.get('Location')
        if loc is None:
            raise RequestErrorException("No Location header in response")

        return CreditNote._getFromURL(loc)
