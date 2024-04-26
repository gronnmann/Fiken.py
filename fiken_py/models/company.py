import datetime
from typing import Optional

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject
from fiken_py.fiken_types import CompanyVatType, Address


class Company(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}'
    _GET_PATH_MULTIPLE = '/companies'

    name: Optional[str] = None
    slug: Optional[str] = None
    organizationNumber: Optional[str] = None
    vatType: Optional[CompanyVatType] = None
    address: Optional[Address] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    creationDate: Optional[str]
    hasApiAccess: Optional[bool] = None
    testCompany: Optional[bool] = None
    accountingStartDate: Optional[datetime.date] = None