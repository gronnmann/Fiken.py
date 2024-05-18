import datetime
from typing import Optional, Literal, Annotated, ClassVar

from pydantic import BaseModel, Field

from fiken_py.fiken_object import FikenObject, FikenObjectRequest, RequestMethod, FikenObjectPaymentPaymentable, \
    FikenObjectAttachable

from fiken_py.shared_types import OrderLine, Payment, Attachment, Note, AccountingAccountAssets
from fiken_py.shared_enums import SaleKind
from fiken_py.models import Contact, Project


class SaleBase(BaseModel):
    saleNumber: Optional[str] = None
    totalPaid: Optional[int] = None
    totalPaidInCurrency: Optional[int] = None
    dueDate: Optional[datetime.date] = None
    kid: Optional[str] = Field(None, min_length=2, max_length=25)
    paymentAccount: Optional[AccountingAccountAssets] = None
    paymentDate: Optional[datetime.date] = None


class Sale(FikenObjectAttachable, FikenObjectPaymentPaymentable, SaleBase):
    _GET_PATH_SINGLE = '/companies/{companySlug}/sales/{saleId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/sales'

    saleId: Optional[int] = None
    lastModifiedDate: Optional[datetime.date] = None
    transactionId: Optional[int] = None
    date: Optional[datetime.date] = None
    kind: Optional[SaleKind] = None
    netAmount: Optional[int] = None
    vatAmount: Optional[int] = None
    settled: Optional[bool] = None
    settledDate: Optional[datetime.date] = None
    writeOff: Optional[bool] = None
    outstandingBalance: Optional[int] = None
    lines: Optional[list[OrderLine]] = None
    customer: Optional[Contact] = None
    currency: Optional[str] = Field(pattern=r"^[A-Z]{3}$")
    salePayments: Optional[list[Payment]] = []
    saleAttachments: Optional[list[Attachment]] = []
    project: Optional[Project] = None
    notes: Optional[list[Note]] = None
    deleted: Optional[bool] = None

    def _refresh_object(self, **kwargs):
        return self._refresh_object(saleId=self.saleId, **kwargs)

class SaleRequest(FikenObjectRequest, SaleBase):
    BASE_CLASS: ClassVar[FikenObject] = Sale
    _POST_PATH = '/companies/{companySlug}/sales/'

    date: datetime.date
    kind: SaleKind
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    lines: list[OrderLine]

    customerId: Optional[int] = None
    paymentFee: Optional[int] = None
    projectId: Optional[str] = None