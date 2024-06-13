from datetime import date
from typing import Optional, ClassVar

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObjectRequiringRequest
from fiken_py.models.journal_entry import JournalEntry


class Transaction(BaseModel, FikenObjectRequiringRequest):
    _GET_PATH_SINGLE = "/companies/{companySlug}/transactions/{transactionId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/transactions/"
    _POST_PATH = "/companies/{companySlug}/generalJournalEntries"

    transactionId: Optional[int] = None
    createdDate: Optional[date] = None
    lastModifiedDate: Optional[date] = None
    description: Optional[str] = None
    type: Optional[str] = None
    entries: list[JournalEntry] = []

    @property
    def id_attr(self):
        return "transactionId", self.transactionId

    def _to_request_object(self, open: Optional[bool] = True, **kwargs) -> BaseModel:
        return JournalEntryRequest(
            open=open,
            journalEntries=self.entries,
            **FikenObjectRequiringRequest._pack_common_fields(self, JournalEntryRequest)
        )


class JournalEntryRequest(BaseModel):
    description: Optional[str] = None
    open: Optional[bool] = False
    journalEntries: list[JournalEntry]
