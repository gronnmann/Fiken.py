from datetime import date
from typing import Optional, ClassVar

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, FikenObjectRequest
from fiken_py.models.journal_entry import JournalEntry


class Transaction(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/transactions/{transactionId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/transactions/'

    transactionId: Optional[int] = None
    createdDate: Optional[date] = None
    lastModifiedDate: Optional[date] = None
    description: Optional[str] = None
    type: Optional[str] = None
    entries: Optional[list[JournalEntry]] = []

    @property
    def id_attr(self):
        return "transactionId", self.transactionId


class JournalEntryRequest(BaseModel, FikenObjectRequest):
    # TODO - move this to own class?
    BASE_CLASS: ClassVar[FikenObject] = Transaction
    _POST_PATH = '/companies/{companySlug}/generalJournalEntries'

    description: Optional[str] = None
    open: Optional[bool] = False
    journalEntries: list[JournalEntry]