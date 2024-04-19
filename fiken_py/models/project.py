from datetime import date
from typing import Optional, ClassVar

from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, FikenObjectRequest
from fiken_py.models import Contact


class ProjectBase(BaseModel):
    number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[date] = None
    completed: Optional[bool] = None


class Project(FikenObject, ProjectBase):
    _GET_PATH_SINGLE = '/companies/{companySlug}/projects/{projectId}'
    _GET_PATH_MULTIPLE = '/companies/{companySlug}/projects/'
    _DELETE_PATH = '/companies/{companySlug}/projects/{projectId}'

    projectId: Optional[int] = None

    startDate: Optional[date] = None

    contact: Optional[Contact] = None
    completed: Optional[bool] = None

    @property
    def is_new(self):
        return self.projectId is None


class ProjectRequest(FikenObjectRequest, ProjectBase):
    BASE_CLASS: ClassVar[FikenObject] = Project
    _POST_PATH = '/companies/{companySlug}/projects'

    startDate: date
    contactId: Optional[int] = None
    name: str
    number: str
