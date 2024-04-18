from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject
from fiken_py.fiken_types import Address, Attachment
from fiken_py.models import ContactPerson


class Contact(BaseModel, FikenObject):
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
    notes: List[str] = []
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
