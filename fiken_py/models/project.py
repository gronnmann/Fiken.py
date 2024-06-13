from __future__ import annotations

import typing
from datetime import date
from typing import Optional, ClassVar, Any

from pydantic import BaseModel

from fiken_py.errors import RequestWrongMediaTypeException, RequestErrorException
from fiken_py.fiken_object import (
    FikenObject,
    RequestMethod,
    FikenObjectRequiringRequest,
    OptionalAccessToken,
)
from fiken_py.models import Contact


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[date] = None
    completed: Optional[bool] = None
    projectId: Optional[int] = None
    startDate: Optional[date] = None


class Project(FikenObjectRequiringRequest, BaseModel):
    _GET_PATH_SINGLE = "/companies/{companySlug}/projects/{projectId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/projects/"
    _DELETE_PATH = "/companies/{companySlug}/projects/{projectId}"
    _PATCH_PATH = "/companies/{companySlug}/projects/{projectId}"
    _POST_PATH = "/companies/{companySlug}/projects"

    name: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[date] = None
    projectId: Optional[int] = None
    number: Optional[str] = None
    startDate: Optional[date] = None
    contact: Optional[Contact] = None
    completed: Optional[bool] = None

    @property
    def id_attr(self):
        return "projectId", self.projectId

    def save(self, token: OptionalAccessToken = None, **kwargs: Any) -> typing.Self:
        if self.is_new:
            return super().save(token=token, **kwargs)

        if self._get_method_base_URL(RequestMethod.PATCH) is None:
            raise RequestWrongMediaTypeException(
                f"Object {self.__class__.__name__} does not support PATCH"
            )

        payload = self._to_request_object()

        try:
            response = self._execute_method(
                RequestMethod.PATCH,
                dumped_object=payload,
                projectId=self.projectId,
                token=token,
                **kwargs,
            )
        except RequestErrorException:
            raise

        return self._follow_location_and_update_class(response)

    def _to_request_object(self, **kwargs) -> BaseModel:
        return ProjectRequest(
            contactId=self.contact.contactId if self.contact is not None else None,
            **FikenObjectRequiringRequest._pack_common_fields(self, ProjectRequest),
        )


class ProjectRequest(BaseModel):
    startDate: date
    name: str
    number: str

    contactId: Optional[int] = None
    description: Optional[str] = None
    endDate: Optional[date] = None
    completed: Optional[bool] = None
