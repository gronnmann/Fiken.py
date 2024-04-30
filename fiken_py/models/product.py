from datetime import date
from typing import Optional

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject
from fiken_py.shared_types import VatTypeProduct, AccountingAccountIncome


class Product(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/products/{productId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/products/'
    _POST_PATH = '/companies/{companySlug}/products/'
    _PUT_PATH = '/companies/{companySlug}/products/{productId}'
    _DELETE_PATH = '/companies/{companySlug}/products/{productId}'

    productId: Optional[int] = None
    name: str
    createdDate: Optional[date] = None
    lastModifiedDate: Optional[date] = None
    unitPrice: Optional[int] = None
    incomeAccount: Optional[AccountingAccountIncome] = None
    vatType: VatTypeProduct
    active: bool = True
    productNumber: Optional[str] = None
    stock: Optional[float] = None
    notes: Optional[str] = None

    @property
    def is_new(self) -> None | bool:
        return self.productId is None
