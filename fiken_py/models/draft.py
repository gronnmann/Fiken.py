import datetime
from typing import Optional, ClassVar, Any

from pydantic import BaseModel, Field

from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import FikenObjectRequest, FikenObject, T, RequestMethod, FikenObjectAttachable
from fiken_py.fiken_types import DraftType, DraftLine, Attachment
from fiken_py.models import Contact, Invoice


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
    bankAccountNumber: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    paymentAccount: Optional[str] = None


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

    def create_object(self):
        if self.CREATED_OBJECT_CLASS is None:
            raise NotImplementedError(f"Object {self.__class__.__name__} does not have a TARGET_CLASS specified")

        url = self._get_method_base_URL("CREATE_OBJECT")
        if url is None:
            raise NotImplementedError(f"Object {self.__class__.__name__} does not have a CREATE_OBJECT path specified")

        try:
            response = self._execute_method(RequestMethod.POST, url, draftId=self.draftId)
        except RequestErrorException:
            raise

        return self._follow_location_and_update_class(response)


class DraftCreateRequest(FikenObjectRequest, DraftBase):
    BASE_CLASS: ClassVar[FikenObject] = Draft

    type: DraftType
    daysUntilDueDate: int
    customerId: int

    contactPersonId: Optional[int] = None


class InvoiceDraft(Draft):
    _GET_PATH_SINGLE = '/companies/{companySlug}/invoices/drafts/{draftId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/invoices/drafts'
    _DELETE_PATH = '/companies/{companySlug}/invoices/drafts/{draftId}'

    _CREATE_OBJECT_PATH = '/companies/{companySlug}/invoices/drafts/{draftId}/createInvoice'
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = Invoice

    type: DraftType = DraftType.INVOICE


class InvoiceDraftCreateRequest(DraftCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = InvoiceDraft
    _POST_PATH = '/companies/{companySlug}/invoices/drafts'

    type: DraftType = DraftType.INVOICE
