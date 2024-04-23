import datetime
from typing import Optional, ClassVar, Any, TypeVar

import requests
from pydantic import BaseModel, Field

from fiken_py.errors import UnsupportedMethodException
from fiken_py.fiken_object import FikenObject, FikenObjectRequest, RequestMethod, T
from fiken_py.fiken_types import VatTypeProduct, Address, Attachment, InvoiceLineRequest, InvoiceLine, \
    SendInvoiceMethod, SendInvoiceEmailOption
from fiken_py.models import Contact, Project, Sale

Inv = TypeVar('Inv', bound='Invoice')


class InvoiceSendRequest(BaseModel):
    method: list[SendInvoiceMethod]
    invoiceId: int
    includeDocumentAttachments: bool

    recipientName: Optional[str] = None
    recipientEmail: Optional[str] = None
    message: Optional[str] = None
    emailSendOption: Optional[SendInvoiceEmailOption] = None  # TODO - requuire this when method is email
    mergeInvoiceAndAttachments: Optional[bool] = None
    organizationNumber: Optional[str] = None
    mobileNumber: Optional[str] = None


class InvoiceUpdateRequest(BaseModel):
    newDueDate: Optional[datetime.date] = None
    sentManually: Optional[bool] = None


class Invoice(FikenObject, BaseModel):
    _GET_PATH_SINGLE = '/companies/{companySlug}/invoices/{invoiceId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/invoices'
    _PATCH_PATH = '/companies/{companySlug}/invoices/{invoiceId}'

    COUNTER_PATH: ClassVar[str] = '/companies/{companySlug}/invoices/counter'

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

    def save(self, **kwargs: Any) -> Inv | None:
        if self._get_method_base_URL(RequestMethod.PATCH) is None:
            raise UnsupportedMethodException(f"Object {self.__class__.__name__} does not support PATCH")

        payload = InvoiceUpdateRequest(**self.dict(exclude_unset=True))
        response = self._execute_method(RequestMethod.PATCH, dumped_object=payload,
                                        invoiceId=self.invoiceId, **kwargs)

        response.raise_for_status()

        return self._follow_location_and_update_class(response)

    @classmethod
    def send_to_customer(cls, invoice_request: InvoiceSendRequest, companySlug=None):
        url = cls._get_method_base_URL(RequestMethod.GET_MULTIPLE) + "/send"

        response = cls._execute_method(RequestMethod.POST, url, dumped_object=invoice_request, companySlug=companySlug,)

        if response.status_code != 200:
            return False
        return True

    @classmethod
    def get_counter(cls) -> int:
        url = cls.PATH_BASE + cls.COUNTER_PATH
        response = cls._execute_method(RequestMethod.GET, url)

        return response.json()['value']

    @classmethod
    def set_initial_counter(cls, counter: int) -> bool:
        """Set the default invoice counter to the given value
        :param counter: The value to set the counter to
        :return: True if the counter was set successfully, False otherwise"""
        url = cls.PATH_BASE + cls.COUNTER_PATH
        response = cls._execute_method(RequestMethod.POST, url, dumped_object=dict({"value": counter}))

        if response.status_code != 201:
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
