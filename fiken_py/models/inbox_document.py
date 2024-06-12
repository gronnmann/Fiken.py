import os
from datetime import datetime
from typing import Optional, ClassVar

import requests
from pydantic import BaseModel

from fiken_py.authorization import AccessToken
from fiken_py.fiken_object import FikenObject, FikenObjectRequest, RequestMethod, OptionalAccessToken


class InboxDocument(BaseModel, FikenObject):
    _GET_PATH_SINGLE = '/companies/{companySlug}/inbox/{inboxDocumentId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/inbox/'

    documentId: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None
    status: Optional[bool] = None
    createdDate: Optional[datetime] = None

    @property
    def id_attr(self):
        return "inboxDocumentId", self.documentId


class InboxDocumentRequest(FikenObjectRequest, BaseModel):
    BASE_CLASS: ClassVar[FikenObject] = InboxDocument
    _POST_PATH = '/companies/{companySlug}/inbox/'

    name: str
    filename: str
    description: str
    file: bytes

    @classmethod
    def from_filepath(cls, name: str, filepath: str, description: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} does not exist")

        with open(filepath, 'rb') as f:
            return cls(name=name, filename=filepath, description=description, file=f.read())

    def save(self, token: OptionalAccessToken = None, **kwargs):
        file_data = {
            'file': (self.filename, self.file),
            'filename': (None, self.filename),
            'description': (None, self.description),
            'name': (None, self.name)
        }

        response = self._execute_method(RequestMethod.POST, file_data=file_data, token=token, **kwargs)

        return self._follow_location_and_update_class(response, token=token, companySlug=self._company_slug)
