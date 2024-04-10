from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject
from fiken_py.fiken_types import VatType, Address


class Company(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}'
    _GET_PATH_MULTIPLE = '/companies'

    name: str
    slug: str
    organizationNumber: str
    vatType: VatType
    address: Address
    phoneNumber: str
    email: str
    creationDate: str # TODO - date type
    hasApiAccess: bool
    testCompany: bool
    accountingStartDate: str # TODO - date type