import datetime
from typing import Optional, List, ClassVar

from pydantic import BaseModel, Field, model_validator

from fiken_py.fiken_object import (
    FikenObjectAttachable,
    FikenObjectRequest,
    FikenObject,
    FikenObjectDeleteFlagable,
    FikenObjectPaymentable,
)
from fiken_py.models import Contact, Project
from fiken_py.models.draft import DraftOrder, DraftOrderCreateRequest
from fiken_py.shared_enums import PurchaseKind, VatTypeProductPurchase
from fiken_py.shared_types import OrderLine, Attachment, AccountingAccount
from fiken_py.models.payment import Payment


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
    paymentAccount: Optional[AccountingAccount] = None
    paymentDate: Optional[datetime.date] = None


class Purchase(
    FikenObjectAttachable,
    FikenObjectDeleteFlagable,
    FikenObjectPaymentable,
    PurchaseBase,
):
    _GET_PATH_SINGLE = "/companies/{companySlug}/purchases/{purchaseId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/purchases"
    _DELETE_PATH = "/companies/{companySlug}/purchases/{purchaseId}/delete"

    _PAYMENTS_PATH = "/companies/{companySlug}/purchases/{purchaseId}/payments"
    _PAYMENTS_SINGLE_PATH = (
        "/companies/{companySlug}/purchases/{purchaseId}/payments/{paymentId}"
    )

    purchaseId: Optional[int] = None
    supplier: Optional[Contact] = None
    payments: Optional[list[Payment]] = []
    purchaseAttachments: Optional[list[Attachment]] = None
    project: Optional[List[Project]] = None
    deleted: Optional[bool] = None

    @property
    def id_attr(self):
        return "purchaseId", self.purchaseId


class PurchaseRequest(FikenObjectRequest, PurchaseBase):
    _POST_PATH = "/companies/{companySlug}/purchases/"
    BASE_CLASS: ClassVar[FikenObject] = Purchase

    supplierId: Optional[int] = None
    projectId: Optional[int] = None

    @model_validator(mode="after")
    @classmethod
    def payment_defails_if_cash_purchase(cls, value):
        if value.kind == PurchaseKind.CASH_PURCHASE:
            assert (
                value.paymentAccount is not None
            ), "paymentAccount must be provided for cash purchases"
            assert (
                value.paymentDate is not None
            ), "paymentDate must be provided for cash purchases"

        return value

    @model_validator(mode="after")
    @classmethod
    def supplier_id_if_not_cash_purchase(cls, value):
        if value.kind != PurchaseKind.CASH_PURCHASE:
            assert (
                value.supplierId is not None
            ), "supplierId must be provided for non-cash purchases"

        return value


class PurchaseDraft(DraftOrder):
    _GET_PATH_SINGLE = "/companies/{companySlug}/purchases/drafts/{draftId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/purchases/drafts"
    _DELETE_PATH = "/companies/{companySlug}/purchases/drafts/{draftId}"
    _PUT_PATH = "/companies/{companySlug}/purchases/drafts/{draftId}"

    _CREATE_OBJECT_PATH = (
        "/companies/{companySlug}/purchases/drafts/{draftId}/createPurchase"
    )
    CREATED_OBJECT_CLASS: ClassVar[FikenObject] = Purchase


class PurchaseDraftRequest(DraftOrderCreateRequest):
    BASE_CLASS: ClassVar[FikenObject] = PurchaseDraft
    _POST_PATH = "/companies/{companySlug}/purchases/drafts"

    @model_validator(mode="after")
    @classmethod
    def correct_vat_type(cls, value):
        for line in value.lines:
            try:
                VatTypeProductPurchase(line.vatType)
                return value
            except ValueError:
                raise ValueError(
                    "Only VatTypeProductPurchase is allowed for sale drafts"
                )
