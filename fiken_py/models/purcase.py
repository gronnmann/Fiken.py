import datetime
from typing import Optional

from pydantic import BaseModel, Field

from fiken_py.fiken_object import FikenObjectAttachable, FikenObjectRequest
from fiken_py.models import Contact
from fiken_py.shared_enums import PurcaseKind
from fiken_py.shared_types import OrderLine


class PurcaseBase(BaseModel):
    date: datetime.date
    kind: PurcaseKind
    paid: bool
    lines: list[OrderLine]
    currency: str = Field(pattern=r"^[A-Z]{3}$")

    purcaseId: Optional[int] = None
    transactionId: Optional[int] = None
    identifier: Optional[str] = None
    dueDate: Optional[datetime.date] = None
    supplier: Optional[Contact] = None
    paymentAccount: Optional[str] = None


class Purcase(FikenObjectAttachable, PurcaseBase):
    pass

class PurcaseRequest(FikenObjectRequest, PurcaseBase):
    pass