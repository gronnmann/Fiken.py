from enum import Enum


class AttachmentType(str, Enum):
    INVOICE = 'invoice'
    REMINDER = 'reminder'
    UNSPECIFIED = 'unspecified'
    OCR = 'ocr'
    BANK_STATEMENT = 'bank_statement'


class SaleKind(str, Enum):
    CASH_SALE = 'cash_sale'
    INVOICE = 'invoice'
    EXTERNAL_INVOICE = 'external_invoice'


class SendMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    EHF = "ehf"
    EFAKTURA = "efaktura"
    LETTER = "letter"
    AUTO = "auto"


class SendEmailOption(str, Enum):
    DOCUMENT_LINK = "document_link"
    ATTACHMENT = "attachment"
    AUTO = "auto"
