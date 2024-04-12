from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject
from fiken_py.fiken_types import Address, ContactPerson, Attachment


class Contact(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/contacts/{contactId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/contacts/'
    _POST_PATH = '/companies/{companySlug}/contacts/'
    _PUT_PATH = '/companies/{companySlug}/contacts/{contactId}'
    _DELETE_PATH = '/companies/{companySlug}/contacts/{contactId}'

    contactId: int = None
    createdDate: date = None
    lastModifiedDate: date = None
    name: str
    email: Optional[str] = None
    organizationNumber: Optional[str] = None
    customerNumber: Optional[int] = None
    customerAccountCode: Optional[str] = None
    phoneNumber: Optional[str] = None
    memberNumber: Optional[float] = None
    supplierNumber: Optional[int] = None
    supplierAccountCode: Optional[str] = None
    customer: bool = False
    supplier: bool = False
    bankAccountNumber: Optional[str] = None
    contactPerson: List[ContactPerson] = []
    notes: List[str] = []
    currency: Optional[str] = None
    language: Optional[str] = None
    inactive: bool = False
    daysUntilInvoicingDueDate: Optional[int] = None
    address: Address = None
    groups: list[str] = []
    documents: List[Attachment] = []