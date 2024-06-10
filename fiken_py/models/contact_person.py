import typing
from typing import Optional, Any

from pydantic import BaseModel

from fiken_py.authorization import AccessToken
from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import FikenObject
from fiken_py.shared_types import Address


class ContactPerson(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/contacts/{contactId}/contactPerson/{contactPersonId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/contacts/{contactId}/contactPerson/'
    _POST_PATH = '/companies/{companySlug}/contacts/{contactId}/contactPerson/'
    _PUT_PATH = '/companies/{companySlug}/contacts/{contactId}/contactPerson/{contactPersonId}'
    _DELETE_PATH = '/companies/{companySlug}/contacts/{contactId}/contactPerson/{contactPersonId}'

    contactPersonId: Optional[int] = None
    name: str
    email: str
    phoneNumber: Optional[str] = None
    address: Optional[Address] = None

    @property
    def id_attr(self):
        return "contactPersonId", self.contactPersonId

    @property
    def is_new(self):
        return self.contactPersonId is None