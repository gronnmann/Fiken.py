from __future__ import annotations

from datetime import date
from typing import Optional, ClassVar, Any, TypeVar

from pydantic import BaseModel

from fiken_py.errors import RequestWrongMediaTypeException
from fiken_py.fiken_object import FikenObject, FikenObjectRequest, T, RequestMethod
from fiken_py.models import Contact

Proj = TypeVar('Proj', bound='Project')

class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[date] = None
    completed: Optional[bool] = None


class ProjectUpdateRequest(ProjectBase):
    projectId: Optional[int] = None
    startDate: Optional[date] = None


class Project(FikenObject, ProjectBase):
    _GET_PATH_SINGLE = '/companies/{companySlug}/projects/{projectId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/projects/'
    _DELETE_PATH = '/companies/{companySlug}/projects/{projectId}'
    _PATCH_PATH = '/companies/{companySlug}/projects/{projectId}'

    projectId: Optional[int] = None
    number: Optional[str] = None
    startDate: Optional[date] = None

    contact: Optional[Contact] = None
    completed: Optional[bool] = None

    @property
    def is_new(self):
        return self.projectId is None

    def save(self, **kwargs: Any) -> Proj | None:
        if self._get_method_base_URL(RequestMethod.PATCH) is None:
            raise RequestWrongMediaTypeException(f"Object {self.__class__.__name__} does not support PATCH")

        payload = ProjectUpdateRequest(**self.dict(exclude_unset=True))
        response = self._execute_method(RequestMethod.PATCH, dumped_object=payload, projectId=self.projectId, **kwargs)

        response.raise_for_status()

        return self._follow_location_and_update_class(response)


class ProjectRequest(FikenObjectRequest, ProjectBase):
    BASE_CLASS: ClassVar[FikenObject] = Project
    _POST_PATH = '/companies/{companySlug}/projects'

    startDate: date
    contactId: Optional[int] = None
    name: str
    number: str
