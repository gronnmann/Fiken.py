from datetime import datetime
from typing import Optional, ClassVar

import requests
from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, FikenObjectRequest, RequestMethod


class InboxDocument(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/inbox/{inboxDocumentId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/inbox/'

    documentId: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None
    status: Optional[bool] = None
    createdDate: Optional[datetime] = None


class InboxDocumentRequest(FikenObjectRequest, BaseModel):
    BASE_CLASS: ClassVar[FikenObject] = InboxDocument
    _POST_PATH = '/companies/{companySlug}/inbox/'

    name: str
    filename: str
    description: str
    file: bytes

    @classmethod
    def from_filename(cls, name: str, filename: str, description: str):
        with open(filename, 'rb') as f:
            return cls(name=name, filename=filename, description=description, file=f.read())

    def save(self, **kwargs):
        if self._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        # using multipart/form-data

        url = self._get_method_base_URL(RequestMethod.POST)

        url = self._preprocess_placeholders(url)
        url, kwargs = self._extract_placeholders(url, **kwargs)

        headers = self._HEADERS.copy()
        headers.pop("Content-Type")

        # send request
        response = requests.post(url, headers=headers, files={
            'file': (self.filename, self.file),
            'filename': (None, self.filename),
            'description': (None, self.description),
            'name': (None, self.name)
        })

        return self._follow_location_and_update_class(response)
