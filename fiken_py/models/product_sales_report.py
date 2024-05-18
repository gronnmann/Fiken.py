from datetime import date
from typing import ClassVar, Optional, List, Any

from pydantic import BaseModel, Field

from fiken_py.fiken_object import FikenObject, FikenObjectRequest, T
from fiken_py.shared_types import ProductSalesLine
from fiken_py.models import Product


class ProductSalesReport(BaseModel, FikenObject):
    product: Optional[Product] = None
    sold: Optional[ProductSalesLine] = None
    credited: Optional[ProductSalesLine] = None
    sum: Optional[ProductSalesLine] = None

    pass
    # TODO - handle weird getting of this class


class ProductSalesReportRequest(BaseModel, FikenObjectRequest):
    BASE_CLASS: ClassVar[List[FikenObject]] = [ProductSalesReport]

    from_: date = Field(..., alias='from')
    to: date

    _POST_PATH = '/companies/{companySlug}/products/salesReport'
