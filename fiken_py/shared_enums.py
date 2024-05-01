from enum import Enum


class CaseInsensitiveEnum(str, Enum):
    """Enum that matches values case-insensitively.
    Used in places API returns values non-consistently."""

    @classmethod
    def _missing_(cls, value: str):
        for member in cls:
            if member.upper() == value.upper():
                return member
        return None


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


class VatTypeProduct(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'


class VatTypeProductSale(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'

    EXEMPT_IMPORT_EXPORT = 'EXEMPT_IMPORT_EXPORT'
    EXEMPT = 'EXEMPT'
    OUTSIDE = 'OUTSIDE'
    EXEMPT_REVERSE = 'EXEMPT_REVERSE'


class VatTypeProductPurcase(CaseInsensitiveEnum):
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    RAW_FISH = 'RAW_FISH'

    HIGH_DIRECT = 'HIGH_DIRECT'
    HIGH_BASIS = 'HIGH_BASIS'
    MEDIUM_DIRECT = 'MEDIUM_DIRECT'
    MEDIUM_BASIS = 'MEDIUM_BASIS'
    NONE_IMPORT_BASIS = 'NONE_IMPORT_BASIS'
    HIGH_FOREIGN_SERVICE_DEDUCTIBLE = 'HIGH_FOREIGN_SERVICE_DEDUCTIBLE'
    HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE = 'HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE'
    LOW_FOREIGN_SERVICE_DEDUCTIBLE = 'LOW_FOREIGN_SERVICE_DEDUCTIBLE'
    LOW_FOREIGN_SERVICE_NONDEDUCTIBLE = 'LOW_FOREIGN_SERVICE_NONDEDUCTIBLE'
    HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE = 'HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE'
    HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE = 'HIGH_PURCASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE'


class CompanyVatType(str, Enum):
    NO = 'no'
    YEARLY = 'yearly'
    MONTHLY = 'monthly'
    BI_MONTHLY = 'bi-monthly'
