from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject


class Invoice(FikenObject, BaseModel):
    pass


class InvoiceRequest(FikenObject, BaseModel):
    pass

class InvoiceLineRequest(BaseModel):
    pass

class InvoiceLine(BaseModel):
    pass