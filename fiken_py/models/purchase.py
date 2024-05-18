import datetime
from typing import Optional, List, ClassVar, TypeVar

from pydantic import BaseModel, Field, model_validator

from fiken_py.errors import RequestErrorException
from fiken_py.fiken_object import FikenObjectAttachable, FikenObjectRequest, FikenObject, RequestMethod, \
    FikenObjectPaymentPaymentable
from fiken_py.models import Contact, Project
from fiken_py.shared_enums import PurchaseKind
from fiken_py.shared_types import OrderLine, Attachment, Payment

Purch = TypeVar('Purch', bound='Purchase')


class PurchaseBase(BaseModel):
    date: datetime.date
    kind: PurchaseKind
    paid: bool
    lines: list[OrderLine]
    currency: str = Field(pattern=r"^[A-Z]{3}$")

    transactionId: Optional[int] = None
    identifier: Optional[str] = None
    dueDate: Optional[datetime.date] = None
    kid: Optional[str] = None
    paymentAccount: Optional[str] = None
    paymentDate: Optional[datetime.date] = None


class Purchase(FikenObjectAttachable, FikenObjectPaymentPaymentable, PurchaseBase):
    _GET_PATH_SINGLE = '/companies/{companySlug}/purchases/{purchaseId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/purchases'
    _DELETE_PATH = '/companies/{companySlug}/purchases/{purchaseId}/delete'

    _PAYMENTS_PATH = '/companies/{companySlug}/purchases/{purchaseId}/payments'
    _PAYMENTS_SINGLE_PATH = '/companies/{companySlug}/purchases/{purchaseId}/payments/{paymentId}'

    purchaseId: Optional[int] = None
    supplier: Optional[Contact] = None
    payments: Optional[list[Payment]] = []
    purchaseAttachments: Optional[list[Attachment]] = None
    project: Optional[List[Project]] = None
    deleted: Optional[bool] = None

    def _refresh_object(self, **kwargs):
        return self._refresh_object(purchaseId=self.purchaseId, **kwargs)


class PurchaseRequest(FikenObjectRequest, PurchaseBase):
    _POST_PATH = '/companies/{companySlug}/purchases/'
    BASE_CLASS: ClassVar[FikenObject] = Purchase

    supplierId: Optional[int] = None
    projectId: Optional[int] = None

    @model_validator(mode="after")
    @classmethod
    def payment_defails_if_cash_purchase(cls, value):
        if value.kind == PurchaseKind.CASH_PURCHASE:
            assert value.paymentAccount is not None, "paymentAccount must be provided for cash purchases"
            assert value.paymentDate is not None, "paymentDate must be provided for cash purchases"

        return value

    @model_validator(mode="after")
    @classmethod
    def supplier_id_if_not_cash_purchase(cls, value):
        if value.kind != PurchaseKind.CASH_PURCHASE:
            assert value.supplierId is not None, "supplierId must be provided for non-cash purchases"

        return value