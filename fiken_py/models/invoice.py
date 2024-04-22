import datetime
from typing import Optional, ClassVar

import requests
from pydantic import BaseModel, Field

from fiken_py.fiken_object import FikenObject, FikenObjectRequest, RequestMethod
from fiken_py.fiken_types import VatTypeProduct, Address, Attachment, InvoiceLineRequest, InvoiceLine, \
    SendInvoiceMethod, SendInvoiceEmailOption
from fiken_py.models import Contact, Project, Sale


class SendInvoiceRequest(BaseModel):
    method: list[SendInvoiceMethod]
    invoiceId: int
    includeDocumentAttachments: bool

    recipientName: Optional[str] = None
    recipientEmail: Optional[str] = None
    message: Optional[str] = None
    emailSendOption: Optional[SendInvoiceEmailOption] = None # TODO - requuire this when method is email
    mergeInvoiceAndAttachments: Optional[bool] = None
    organizationNumber: Optional[str] = None
    mobileNumber: Optional[str] = None


class Invoice(FikenObject, BaseModel):
    _GET_PATH_SINGLE = '/companies/{companySlug}/invoices/{invoiceId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/invoices'

    invoiceId: Optional[int] = None
    createdDate: Optional[datetime.date] = None
    lastModifiedDate: Optional[datetime.date] = None
    invoiceNumber: Optional[int] = None
    kid: Optional[str] = None
    issueDate: Optional[datetime.date] = None
    dueDate: Optional[datetime.date] = None
    originalDueDate: Optional[datetime.date] = None
    net: Optional[int] = None
    vat: Optional[int] = None
    gross: Optional[int] = None
    netInNok: Optional[int] = None
    vatInNok: Optional[int] = None
    grossInNok: Optional[int] = None
    cash: Optional[bool] = None
    invoiceText: Optional[str] = None
    yourReference: Optional[str] = None
    ourReference: Optional[str] = None
    orderReference: Optional[str] = None
    invoiceDraftUuid: Optional[str] = None
    address: Optional[Address] = None
    lines: Optional[list[InvoiceLine]] = []
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    bankAccountNumber: Optional[str] = None
    sentManually: Optional[bool] = None
    invoicePdf: Optional[Attachment] = None
    associatedCreditNotes: Optional[list[int]] = []
    attachments: Optional[list[Attachment]] = []
    customer: Optional[Contact] = None
    sale: Optional[Sale] = None,
    project: Optional[Project] = None

    @classmethod
    def send_to_customer(cls, invoice_request: SendInvoiceRequest, invoice=None, invoiceId=None, companySlug=None):
        url = cls._get_method_base_URL(RequestMethod.GET_MULTIPLE) + "/send"

        if invoice:
            invoiceId = invoice.invoiceId

        response = cls._execute_method(RequestMethod.POST, url, dumped_object=invoice_request, companySlug=companySlug, invoiceId=invoiceId)

        if response.status_code != 200:
            return False
        return True


class InvoiceRequest(FikenObjectRequest, BaseModel):
    _POST_PATH = '/companies/{companySlug}/invoices/'
    BASE_CLASS: ClassVar[FikenObject] = Invoice

    issueDate: datetime.date
    dueDate: datetime.date
    customerId: int
    cash: bool
    bankAccountCode: str

    uuid: Optional[str] = None
    lines: list[InvoiceLineRequest]
    ourReference: Optional[str] = None
    yourReference: Optional[str] = None
    orderReference: Optional[str] = None
    contactPersonId: Optional[int] = None
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    invoiceText: Optional[str] = Field(None, max_length=500)
    paymentAccount: Optional[str] = None  # needs when cash is provided
    projectId: Optional[int] = None
