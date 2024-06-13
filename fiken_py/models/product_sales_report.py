import typing
from datetime import date
from typing import ClassVar, Optional, List, Any

from pydantic import BaseModel, Field, ConfigDict

from fiken_py.fiken_object import (
    FikenObject,
    FikenObjectRequiringRequest,
    RequestMethod,
    OptionalAccessToken,
)
from fiken_py.shared_types import ProductSalesLine
from fiken_py.models import Product


class ProductSalesReport(BaseModel, FikenObject):
    product: Optional[Product] = None
    sold: Optional[ProductSalesLine] = None
    credited: Optional[ProductSalesLine] = None
    sum: Optional[ProductSalesLine] = None

    _POST_PATH = "/companies/{companySlug}/products/salesReport"

    @classmethod
    def get_report_for_timeframe(
        cls, from_: date, to: date, token: OptionalAccessToken = None, **kwargs
    ) -> List[typing.Self]:
        req = ProductSalesReportRequest(
            from_=from_,
            to=to,
        )

        response = cls._execute_method(
            RequestMethod.POST, dumped_object=req, token=token, **kwargs
        )

        return [cls(**report) for report in response.json()]

    @property
    def id_attr(self) -> tuple[str, str | None]:
        return "NONE", None


class ProductSalesReportRequest(BaseModel):
    from_: date = Field(alias="from")
    to: date

    model_config = ConfigDict(
        populate_by_name=True,
    )
