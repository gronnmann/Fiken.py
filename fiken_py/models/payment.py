from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class Payment(FikenObject, BaseModel):
    description: Optional[str] = None
    paymentId: Optional[int] = None
    date: date
    account: str  # TODO - update with account type
    amount: int
    amountInNok: Optional[int] = None
    currency: Optional[str] = None
    fee: Optional[int] = None


class PaymentPurchase(Payment):
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/purchases/{purchaseId}/payments'
    _GET_PATH_SINGLE = '/companies/{companySlug}/purchases/{purchaseId}/payments/{paymentId}'
    _POST_PATH = '/companies/{companySlug}/purchases/{purchaseId}/payments'

    purchaseId: Optional[int] = None


class PaymentSale(Payment):
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/sales/{saleId}/payments'
    _GET_PATH_SINGLE = '/companies/{companySlug}/sales/{saleId}/payments/{paymentId}'
    _POST_PATH = '/companies/{companySlug}/sales/{saleId}/payments'

    saleId: Optional[int] = None
