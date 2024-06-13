import typing
from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from fiken_py.errors import (
    RequestWrongMediaTypeException,
    RequestContentNotFoundException,
)
from fiken_py.fiken_object import FikenObjectAttachable, OptionalAccessToken
from fiken_py.shared_types import Address, Attachment, Note
from fiken_py.models import ContactPerson


class Contact(BaseModel, FikenObjectAttachable):
    _GET_PATH_SINGLE = "/companies/{companySlug}/contacts/{contactId}"
    _GET_PATH_MULTIPLE = "/companies/{companySlug}/contacts/"
    _POST_PATH = "/companies/{companySlug}/contacts/"
    _PUT_PATH = "/companies/{companySlug}/contacts/{contactId}"
    _DELETE_PATH = "/companies/{companySlug}/contacts/{contactId}"

    contactId: Optional[int] = None
    createdDate: Optional[date] = None
    lastModifiedDate: Optional[date] = None
    name: str
    email: Optional[str] = None
    organizationNumber: Optional[str] = None
    customerNumber: Optional[int] = None
    customerAccountCode: Optional[str] = None
    phoneNumber: Optional[str] = None
    memberNumber: Optional[float] = None
    supplierNumber: Optional[int] = None
    supplierAccountCode: Optional[str] = None
    customer: Optional[bool] = False
    supplier: Optional[bool] = False
    bankAccountNumber: Optional[str] = None
    contactPerson: List[ContactPerson] = []
    notes: List[Note] = []
    currency: Optional[str] = None
    language: Optional[str] = None
    inactive: Optional[bool] = False
    daysUntilInvoicingDueDate: Optional[int] = None
    address: Optional[Address] = None
    groups: list[str] = []
    documents: List[Attachment] = []

    @property
    def id_attr(self):
        return "contactId", self.contactId

    @classmethod
    def get_attachments_cls(
        cls,
        instance: Optional[typing.Self] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ) -> list[Attachment]:
        if instance is None:
            if kwargs.get("contactId") is None:
                raise ValueError(
                    "contactId must be provided to get_attachments_cls without instance"
                )
            instance = cls.get(token=token, **kwargs)

            if instance is None:
                raise RequestContentNotFoundException(
                    f"Contact with id {kwargs.get('contactId')} not found. Can't get attachments."
                )

        return instance.documents or []

    def get_attachments(
        self, token: OptionalAccessToken = None, **kwargs
    ) -> list[Attachment]:
        return self.documents

    def add_attachment(
        self,
        filepath,
        filename: Optional[str] = None,
        comment: Optional[str] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        resp = self.add_attachment_cls(
            filepath, filename, comment, instance=self, **kwargs
        )

        if resp:
            self._refresh_object()

        return resp

    def add_attachment_bytes(
        self,
        filename: str,
        data: bytes,
        comment: Optional[str] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        resp = self.add_attachment_bytes_cls(
            filename, data, comment, instance=self, **kwargs
        )

        if resp:
            self._refresh_object()

        return resp

    def get_contact_persons(self, **kwargs) -> List[ContactPerson]:
        return ContactPerson.getAll(
            companySlug=self._company_slug,
            token=self._auth_token,
            contactId=self.contactId,
            **kwargs,
        )

    def get_contact_person(
        self, contact_person_id: int, **kwargs
    ) -> ContactPerson | None:
        return ContactPerson.get(
            contactPersonId=contact_person_id,
            companySlug=self._company_slug,
            token=self._auth_token,
            contactId=self.contactId,
            **kwargs,
        )

    def create_contact_person(
        self, contact_person: ContactPerson, **kwargs
    ) -> ContactPerson:
        person = contact_person.save(
            token=self._auth_token,
            contactId=self.contactId,
            companySlug=self._company_slug,
            **kwargs,
        )
        self._refresh_object()

        return person
