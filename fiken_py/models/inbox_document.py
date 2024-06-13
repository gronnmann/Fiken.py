import os
from datetime import datetime
from typing import Optional, ClassVar

import requests
from pydantic import BaseModel

from fiken_py.authorization import AccessToken
from fiken_py.errors import RequestContentNotFoundException
from fiken_py.fiken_object import (
    FikenObject,
    RequestMethod,
    OptionalAccessToken,
    FikenObjectRequiringRequest,
)


class InboxDocument(BaseModel, FikenObjectRequiringRequest):
    _GET_PATH_SINGLE = "/companies/{companySlug}/inbox/{inboxDocumentId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/inbox/"
    _UPLOAD_PATH = "/companies/{companySlug}/inbox/"

    documentId: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    filename: Optional[str] = None
    status: Optional[bool] = None
    createdDate: Optional[datetime] = None

    @property
    def id_attr(self):
        return "inboxDocumentId", self.documentId

    @classmethod
    def upload_from_filepath(
        cls,
        filepath: str,
        name: str,
        description: str,
        filename: Optional[str] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        if filename is None:
            filename = os.path.basename(filepath)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} does not exist")

        with open(filepath, "rb") as f:
            return cls.upload_from_bytes(
                f.read(), name, description, filename, token=token, **kwargs
            )

    @classmethod
    def upload_from_bytes(
        cls,
        file: bytes,
        name: str,
        description: str,
        filename: str,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        req = InboxDocumentRequest(
            name=name, file=file, description=description, filename=filename
        )

        file_data = req.to_filedata_dict()

        response = cls._execute_method(
            RequestMethod.POST,
            url=cls._get_method_base_URL("UPLOAD"),
            file_data=file_data,
            token=token,
            **kwargs,
        )

        location = response.headers.get("Location")

        if location is None:
            raise RequestContentNotFoundException("No Location header in response")

        return InboxDocument._get_from_url(location, token=token, **kwargs)


class InboxDocumentRequest(BaseModel):
    name: str
    filename: str
    description: str
    file: bytes

    def to_filedata_dict(self) -> dict:
        return {
            "file": (self.filename, self.file),
            "filename": (None, self.filename),
            "description": (None, self.description),
            "name": (None, self.name),
        }
