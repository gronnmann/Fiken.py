import datetime
import typing
from typing import Optional, ClassVar, Any

import requests
from pydantic import BaseModel, Field, model_validator

from fiken_py.errors import RequestWrongMediaTypeException, RequestErrorException
from fiken_py.fiken_object import (
    FikenObject,
    RequestMethod,
    FikenObjectCountable,
    FikenObjectAttachable,
    FikenObjectRequiringRequest,
    OptionalAccessToken,
)
from fiken_py.models.draft import (
    DraftInvoiceIsh,
    DraftTypeInvoiceIsh,
    DraftInvoiceIshRequest,
)
from fiken_py.shared_types import (
    Address,
    Attachment,
    InvoiceLineRequest,
    InvoiceLine,
    BankAccountNumber,
    AccountingAccountAssets,
    AccountingAccount,
)
from fiken_py.shared_enums import SendMethod, SendEmailOption, VatTypeProduct
from fiken_py.models import Contact, Project, Sale


class InvoiceSendRequest(BaseModel):
    method: list[SendMethod]
    invoiceId: int
    includeDocumentAttachments: bool

    recipientName: Optional[str] = None
    recipientEmail: Optional[str] = None
    message: Optional[str] = None
    emailSendOption: Optional[SendEmailOption] = (
        None  # TODO - requuire this when method is email
    )
    mergeInvoiceAndAttachments: Optional[bool] = None
    organizationNumber: Optional[str] = None
    mobileNumber: Optional[str] = None


class InvoiceUpdateRequest(BaseModel):
    newDueDate: Optional[datetime.date] = None
    sentManually: Optional[bool] = None


class Invoice(
    FikenObjectRequiringRequest, FikenObjectCountable, FikenObjectAttachable, BaseModel
):
    _GET_PATH_SINGLE = "/companies/{companySlug}/invoices/{invoiceId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/invoices"
    _PATCH_PATH = "/companies/{companySlug}/invoices/{invoiceId}"
    _POST_PATH = "/companies/{companySlug}/invoices/"

    _COUNTER_PATH = "/companies/{companySlug}/invoices/counter"

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
    lines: list[InvoiceLine] = []
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    bankAccountNumber: Optional[str] = None
    sentManually: Optional[bool] = None
    invoicePdf: Optional[Attachment] = None
    associatedCreditNotes: Optional[list[int]] = []
    attachments: Optional[list[Attachment]] = []
    customer: Optional[Contact] = None
    sale: Optional[Sale] = None
    project: Optional[Project] = None

    @property
    def id_attr(self):
        return "invoiceId", self.invoiceId

    def save(self, token: OptionalAccessToken = None, **kwargs: Any) -> typing.Self:
        if self.is_new:
            return super().save(token=token, **kwargs)

        if self._get_method_base_URL(RequestMethod.PATCH) is None:
            raise RequestWrongMediaTypeException(
                f"Object {self.__class__.__name__} does not support PATCH"
            )

        payload = InvoiceUpdateRequest(
            newDueDate=self.dueDate, sentManually=self.sentManually
        )

        try:
            response = self._execute_method(
                RequestMethod.PATCH,
                dumped_object=payload,
                invoiceId=self.invoiceId,
                **kwargs,
            )
        except RequestErrorException:
            raise

        return self._follow_location_and_update_class(response)

    @classmethod
    def send_to_customer(cls, invoice_request: InvoiceSendRequest, companySlug=None):
        url_base = cls._get_method_base_URL(RequestMethod.GET_MULTIPLE)

        if url_base is None:
            raise RequestWrongMediaTypeException(
                f"Object {cls.__name__} does not support GET_MULTIPLE = used for infering 'send' URL"
            )

        url = url_base + "/send"

        try:
            response = cls._execute_method(
                RequestMethod.POST,
                url,
                dumped_object=invoice_request,
                companySlug=companySlug,
            )
        except RequestErrorException:
            raise

        if response.status_code != 200:
            return False
        return True

    def _to_request_object(
        self,
        bankAccountCode: Optional[AccountingAccountAssets | str] = None,
        uuid: Optional[str] = None,
        paymentAccount: Optional[AccountingAccount | str] = None,
        contactPersonId: Optional[int] = None,
        **kwargs,
    ) -> BaseModel:

        if bankAccountCode is None:
            raise ValueError("bankAccountCode must be provided for saving Invoice")

        lines_request = []
        for line in self.lines:
            lines_request.append(
                InvoiceLineRequest(
                    **line.model_dump(exclude={"grossInNok", "netInNok", "vatInNok"})
                )
            )

        common_lines = FikenObjectRequiringRequest._pack_common_fields(
            self, InvoiceRequest
        )
        common_lines["lines"] = lines_request

        if contactPersonId is None:
            if self.customer is not None and len(self.customer.contactPerson) > 0:
                contactPersonId = self.customer.contactPerson[0].contactPersonId

        return InvoiceRequest(
            bankAccountCode=bankAccountCode,
            uuid=uuid,
            paymentAccount=paymentAccount,
            projectId=self.project.projectId if self.project is not None else None,
            customerId=self.customer.contactId if self.customer is not None else None,
            contactPersonId=contactPersonId,
            **common_lines,
        )


class InvoiceRequest(BaseModel):
    issueDate: datetime.date
    dueDate: datetime.date
    customerId: int
    cash: bool
    bankAccountCode: str

    uuid: Optional[str] = None
    lines: list[InvoiceLineRequest] = Field([], min_length=1)
    ourReference: Optional[str] = None
    yourReference: Optional[str] = None
    orderReference: Optional[str] = None
    contactPersonId: Optional[int] = None
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    invoiceText: Optional[str] = Field(None, max_length=500)
    paymentAccount: Optional[str] = None  # needs when cash is provided
    projectId: Optional[int] = None

    @model_validator(mode="after")
    @classmethod
    def validate_cash_payment_account(cls, value):
        if value.cash is True:
            assert (
                value.paymentAccount is not None
            ), "paymentAccount must be provided for cash payments"
        return value


class InvoiceDraft(DraftInvoiceIsh):
    _GET_PATH_SINGLE = "/companies/{companySlug}/invoices/drafts/{draftId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/invoices/drafts"
    _DELETE_PATH = "/companies/{companySlug}/invoices/drafts/{draftId}"
    _PUT_PATH = "/companies/{companySlug}/invoices/drafts/{draftId}"
    _POST_PATH = "/companies/{companySlug}/invoices/drafts"

    _CREATE_OBJECT_PATH = (
        "/companies/{companySlug}/invoices/drafts/{draftId}/createInvoice"
    )
    CREATED_OBJECT_CLASS: ClassVar[typing.Type[FikenObject]] = Invoice

    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.INVOICE

    def _to_request_object(
        self,
        contactId: Optional[int] = None,
        contactPersonId: Optional[int] = None,
        **kwargs,
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

        return InvoiceDraftRequest(
            customerId=contactId,
            contactPersonId=contactPersonId,
            **FikenObjectRequiringRequest._pack_common_fields(
                self, InvoiceDraftRequest
            ),
        )


class InvoiceDraftRequest(DraftInvoiceIshRequest):
    type: DraftTypeInvoiceIsh = DraftTypeInvoiceIsh.INVOICE
