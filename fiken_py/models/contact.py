from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from fiken_py.errors import RequestWrongMediaTypeException
from fiken_py.fiken_object import FikenObjectAttachable
from fiken_py.shared_types import Address, Attachment, Note
from fiken_py.models import ContactPerson


class Contact(BaseModel, FikenObjectAttachable):
    _GET_PATH_SINGLE = '/companies/{companySlug}/contacts/{contactId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/contacts/'
    _POST_PATH = '/companies/{companySlug}/contacts/'
    _PUT_PATH = '/companies/{companySlug}/contacts/{contactId}'
    _DELETE_PATH = '/companies/{companySlug}/contacts/{contactId}'

    contactId: Optional[int] = None
    createdDate: Optional[date] = None
    lastModifiedDate: Optional[date] = None
    name: str
    email: Optional[str] = None
    organizationNumber: Optional[str] = None
    customerNumber: Optional[int] = None
    customerAccountCode: Optional[str] = None
    phoneNumber: Optional[str] = None
    memberNumber: Optional[float] = None
    supplierNumber: Optional[int] = None
    supplierAccountCode: Optional[str] = None
    customer: Optional[bool] = False
    supplier: Optional[bool] = False
    bankAccountNumber: Optional[str] = None
    contactPerson: Optional[List[ContactPerson]] = []
    notes: List[Note] = []
    currency: Optional[str] = None
    language: Optional[str] = None
    inactive: Optional[bool] = False
    daysUntilInvoicingDueDate: Optional[int] = None
    address: Optional[Address] = None
    groups: list[str] = []
    documents: List[Attachment] = []

    @property
    def is_new(self):
        return self.contactId is None

    @property
    def id_attr(self):
        return "contactId", self.contactId

    @classmethod
    def get_attachments_cls(cls, instance: FikenObjectAttachable = None, **kwargs) -> list[Attachment]:
        return instance.documents

    def get_attachments(self, **kwargs) -> list[Attachment]:
        return self.documents

    def add_attachment(self, filepath, filename: str = None, comment: str = None, **kwargs):
        resp = self.add_attachment_cls(filepath, filename, comment, instance=self, **kwargs)

        if resp:
            self._refresh_object()

        return resp

    def add_attachment_bytes(self, filename: str, data: bytes, comment: str = None, **kwargs):
        resp = self.add_attachment_bytes_cls(filename, data, comment, instance=self, **kwargs)

        if resp:
            self._refresh_object()

        return resp