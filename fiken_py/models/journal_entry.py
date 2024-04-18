from typing import Optional, ClassVar

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, FikenObjectRequest
from fiken_py.fiken_types import Attachment, JournalEntryLine
from datetime import date


class JournalEntry(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/journalEntries/{journalEntryId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/journalEntries/'

    journalEntryId: Optional[int] = None
    createdDate: Optional[date] = None
    lastModifiedDate: Optional[date] = None
    transactionId: Optional[int] = None
    offsetTransactionId: Optional[int] = None
    journalEntryNumber: Optional[int] = None
    description: str
    date: date
    lines: list[JournalEntryLine]
    attachments: Optional[list[Attachment]] = []