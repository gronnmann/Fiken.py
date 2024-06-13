from __future__ import annotations

import abc
import datetime
import logging
import os.path
import re
import time
import typing
import uuid
from enum import Enum
from typing import Any, ClassVar, Optional

import requests
import platform
from importlib.metadata import version

from pydantic import BaseModel, ValidationError

from fiken_py.authorization import AccessToken, Authorization
from fiken_py.errors import (
    RequestConnectionException,
    RequestContentNotFoundException,
    RequestWrongMediaTypeException,
    RequestErrorException,
)
from fiken_py.shared_types import Attachment, Counter
from fiken_py.util import handle_error

logger = logging.getLogger("fiken_py")

type OptionalAccessToken = Optional[AccessToken | str]


class RequestMethod(Enum):
    GET = ("GET",)
    GET_MULTIPLE = ("GET_MULTIPLE",)
    POST = ("POST",)
    PUT = ("PUT",)
    DELETE = ("DELETE",)
    PATCH = ("PATCH",)


class FikenObject:
    """
    Base class for all Fiken objects.
    Every object has a base URL, an authentication token and a path.

    Auth token should be set first before making any requests.

    The PATH_BASE is the URL path to the object. For example, the path for a user object is '/user'.

    Other than that, we have class variables for the path which allow different requests:
    - GET_PATH_SINGLE: The path for getting a single object. Use {placeholder} for the object ID.
    - GET_PATH_MULTIPLE: The path for getting multiple objects.
    - POST_PATH: The path for creating a new object.
    - PUT_PATH: The path for updating an object. Use {placeholder} for the object ID.
    - DELETE_PATH: The path for deleting an object.

    Use {placeholder} for the object ID.
    """

    PATH_BASE: ClassVar[str] = "https://api.fiken.no/api/v2"

    """Authentication token for the session. Can be either personal token or OAuth2 token.
    Can be specified globally for all objects or for each object separately.
    """
    _AUTH_TOKEN: OptionalAccessToken = None

    _COMPANY_SLUG: Optional[str] = None

    _RATE_LIMIT_ENABLED: ClassVar[bool] = True
    _MAX_REQUESTS_PER_SECOND: ClassVar[int] = 4
    _REQUESTS_COUNTER: ClassVar[int] = 0
    _LAST_REQUEST_TIME: ClassVar[int] = 0

    @classmethod
    def set_auth_token(cls, token: OptionalAccessToken):
        """
        Sets the personal authentication token.
        Can be either personal token (str) or OAuth2 token gotten from Authorization class.
        :param token: token to set
        :param credentials: tuple of (client id, client secret) for OAuth2 refreshing
        :return: None
        """

        if cls._AUTH_TOKEN is not None:
            raise ValueError(
                "Some form of authentication token is already set (personal or OAuth2)."
                "Please clear session first (clear_auth_token())."
            )

        cls._AUTH_TOKEN = token

    @classmethod
    def clear_auth_token(cls):
        cls._AUTH_TOKEN = None

    @property
    @abc.abstractmethod
    def id_attr(self) -> tuple[str, str | None]:
        """Returns the ID field (to be used in URLs) and its value for the object."""
        return "UNKNOWN", None

    @classmethod
    def set_company_slug(cls, company_slug):
        cls._COMPANY_SLUG = company_slug

    @classmethod
    def clear_company_slug(cls):
        cls._COMPANY_SLUG = None

    @classmethod
    def set_rate_limit(cls, enabled: bool):
        cls._RATE_LIMIT_ENABLED = enabled

    @classmethod
    def get(
        cls: type[typing.Self], token: OptionalAccessToken = None, **kwargs: Any
    ) -> typing.Self | None:

        try:
            response = cls._execute_method(RequestMethod.GET, token=token, **kwargs)
        except RequestContentNotFoundException as e:
            return None
        except Exception as e:
            raise e

        logger.debug(f"GETting single object for {cls.__name__}")

        data = response.json()
        return cls._inject_token_and_slug_and_return(
            cls(**data), token, kwargs.get("companySlug")
        )

    @classmethod
    def getAll(
        cls,
        token: OptionalAccessToken = None,
        follow_pages: bool = True,
        page: Optional[int] = None,
        **kwargs: Any,
    ) -> list[typing.Self]:

        logger.debug(f"GETting many objects for {cls.__name__}")
        try:
            response = cls._execute_method(
                RequestMethod.GET_MULTIPLE, token=token, **kwargs
            )
        except RequestErrorException as e:
            raise

        if page is not None:
            if follow_pages:
                raise ValueError("Cannot specify page number when follow_pages is True")
            kwargs["page"] = page

        fetched_pages = [response.json()]
        if follow_pages:
            page_count = response.headers.get("Fiken-Api-Page-Count")
            if page_count is not None:
                page_count = int(page_count)
            if page_count is not None and page_count > 1:
                logger.debug(f"Multiple pages found. Fetching {page_count} pages")
                for i in range(1, page_count):
                    try:
                        response = cls._execute_method(
                            RequestMethod.GET_MULTIPLE, page=i, token=token, **kwargs
                        )
                    except RequestErrorException as e:
                        raise

                    fetched_pages.append(response.json())

        objects = []
        for fetched_page in fetched_pages:
            for item in fetched_page:
                obj = cls(**item)
                obj = cls._inject_token_and_slug_and_return(
                    obj, token, kwargs.get("companySlug")
                )
                objects.append(obj)

        return objects

    @classmethod
    def _get_from_url(
        cls, url: str, token: OptionalAccessToken = None, **kwargs
    ) -> typing.Self:
        try:
            response = cls._execute_method(
                RequestMethod.GET, url=url, token=token, **kwargs
            )
        except RequestErrorException:
            raise

        logger.debug(f"GETting single object from URL {url}")

        data = response.json()

        return cls._inject_token_and_slug_and_return(
            cls(**data), token, kwargs.get("companySlug")
        )

    def save(self, token: OptionalAccessToken = None, **kwargs: Any) -> typing.Self:
        """
        Saves the object to the server.
        Checks if object is new or not and sends a POST or PUT request accordingly.
        If object has no method for checking if it is new, assumes POST.
        Throws an exception if object has PUT method defined, but no is new check.

        :param token: Access token to use for the request
        :param kwargs: arguments to replace placeholders in the path
        :return: None or the new object
        """
        if token is None:
            token = self._auth_token

        if kwargs.get("companySlug") is None:
            kwargs["companySlug"] = self._company_slug

        if self._get_method_base_URL(RequestMethod.PUT) is not None:
            if self.is_new is None:
                raise NotImplementedError(
                    f"Object {self.__class__.__name__} has PUT path specified, but no is_new method"
                )

        use_post = self.is_new if self.is_new is not None else True
        used_method = RequestMethod.POST if use_post else RequestMethod.PUT
        dumped_object = self
        if issubclass(self.__class__, FikenObjectRequiringRequest):
            dumped_object = self._to_request_object(**kwargs)

        try:
            response = self._execute_method(
                used_method, token=token, dumped_object=dumped_object, **kwargs
            )
        except RequestErrorException:
            raise

        ret = self._follow_location_and_update_class(response, token, **kwargs)

        if ret is None:
            raise RequestContentNotFoundException("Saved object not found in response")

        return ret

    def _follow_location_and_update_class(
        self: typing.Self,
        response: requests.Response,
        token: OptionalAccessToken = None,
        **kwargs,
    ) -> typing.Self:
        """Follows the location header in the response and returns the new object.
        If new object is of the same class, updates the current object with the new one.
        """
        location = response.headers.get("Location")
        if location:
            logger.debug(f"Location of new object: {location}")

            new_object = self.__class__._get_from_url(location, token, **kwargs)
            self.__dict__.update(new_object.__dict__)

            return self
        else:
            raise RequestContentNotFoundException(
                f"Location header not found in response for {self.__class__.__name__}"
            )

    def _refresh_object(self, **kwargs):
        try:
            id_attr, id_attr_val = self.id_attr

            if kwargs.get(id_attr) is None:
                kwargs[id_attr] = id_attr_val

            if kwargs.get("companySlug") is None:
                kwargs["companySlug"] = self._company_slug

            if kwargs.get("token") is None:
                kwargs["token"] = self._auth_token

            fiken_object = self.get(**kwargs)
        except RequestErrorException as e:
            raise
        self.__dict__.update(fiken_object.__dict__)

    def delete(self, token: OptionalAccessToken = None, **kwargs: Any) -> bool:
        attr_name, attr_val = self.id_attr
        if kwargs.get(attr_name) is None:
            kwargs[attr_name] = attr_val

        if kwargs.get("companySlug") is None:
            kwargs["companySlug"] = self._company_slug

        if token is None:
            token = self._auth_token

        try:
            response = self._execute_method(RequestMethod.DELETE, token=token, **kwargs)
        except RequestErrorException:
            raise

        for attr in self.__dict__:
            setattr(self, attr, None)

        return True

    # TODO - better way to do this?
    _PLACEHOLDER_REGEX = re.compile(r"{(\w+)}")

    @classmethod
    def _extract_placeholders_kwargs(
        cls, path: str, **kwargs: Any
    ) -> tuple[str, dict[str, Any]]:
        """
        Extract placeholders from the path and replace them with the values in kwargs.
        Also fills out companySlug if not provided.
        :returns the formatted path, and the remaining kwargs
        """

        if kwargs.get("companySlug") is None and cls._COMPANY_SLUG is not None:
            kwargs["companySlug"] = cls._COMPANY_SLUG

        placeholders = cls._PLACEHOLDER_REGEX.findall(path)

        for placeholder in placeholders:
            if placeholder not in kwargs:
                raise ValueError(
                    f"Missing placeholder value for {placeholder} in {path}"
                )

        path = path.format(
            **{placeholder: kwargs.pop(placeholder) for placeholder in placeholders}
        )
        return path, kwargs

    @classmethod
    def _extract_placeholders_basemodel(cls, path: str, base_model: BaseModel) -> str:
        """Preprocesses placeholders in the path
        Replaces them with values from the BaseModel

        :param path: URL
        :return: the formatted path
        """

        placeholders = cls._PLACEHOLDER_REGEX.findall(path)

        for placeholder in placeholders:
            if not hasattr(base_model, placeholder):
                continue
            else:
                path = path.replace(
                    f"{{{placeholder}}}", str(getattr(base_model, placeholder))
                )

        return path

    @classmethod
    def _get_method_base_URL(cls, method: RequestMethod | str) -> None | str:
        """Gets the base URL corresponding to the method.
        If the method is unsupported, returns None"""

        if method == RequestMethod.GET:
            attr_name = f"_GET_PATH_SINGLE"
        elif method == RequestMethod.GET_MULTIPLE:
            attr_name = f"_GET_PATH_MULTIPLE"
        else:
            if isinstance(method, RequestMethod):
                attr_base = method.name
            else:
                attr_base = method

            attr_name = f"_{attr_base}_PATH"

        if hasattr(cls, attr_name):
            return f"{cls.PATH_BASE}{getattr(cls, attr_name).default}"
        return None

    @classmethod
    def _execute_method(
        cls,
        method: RequestMethod,
        url: Optional[str] = None,
        dumped_object: Optional[FikenObject | dict | BaseModel] = None,
        file_data: Optional[dict[str, tuple]] = None,
        token: OptionalAccessToken = None,
        trial: int = 0,
        **kwargs: Any,
    ) -> requests.Response:
        """Executes a method on the object
        :method: RequestMethod - the method to execute
        :url: str - the URL to execute the method on. If None, will be generated from the method
        :dumped_object: - the object to send/dump and extract placeholders from. If None, will be ignored
        :file_data: dict - the file data to send. If None, will be ignored
        :trial: int - the number of times the method has been tried
        :kwargs: dict - the arguments to pass to the method
        """

        # Check if token is expired
        if isinstance(token, AccessToken):
            # get datetime as Z-time
            if token.is_expired() and trial == 0:
                try:
                    token.attempt_refresh()
                    return cls._execute_method(
                        method,
                        url,
                        dumped_object,
                        file_data,
                        token,
                        trial + 1,
                        **kwargs,
                    )
                except RequestErrorException as e:
                    logger.error(f"Failed to refresh token: {e}")

        if file_data is not None and method != RequestMethod.POST:
            raise ValueError("Only POST requests can have file data")

        # TODO - maybe re-add this?
        # if file_data is not None and dumped_object is not None:
        #     raise ValueError("Only one of file data and instance can be provided")

        if url is None:
            url = cls._get_method_base_URL(method)

        if token is None:
            if cls._AUTH_TOKEN is None:
                raise ValueError("Auth token not set")
            token = cls._AUTH_TOKEN

        if url is None:
            raise RequestWrongMediaTypeException(
                f"Object {cls.__name__} does not support {method.name}"
            )

        if issubclass(dumped_object.__class__, BaseModel):
            url = cls._extract_placeholders_basemodel(url, dumped_object)

        url, kwargs = cls._extract_placeholders_kwargs(url, **kwargs)

        method_name = method.name
        if method == RequestMethod.GET_MULTIPLE:
            method_name = "GET"

        request_data: Optional[str | dict] = None

        if dumped_object is not None:
            if method not in [
                RequestMethod.POST,
                RequestMethod.PUT,
                RequestMethod.PATCH,
            ]:
                raise ValueError(
                    "Only POST, PUT and PATCH requests can have an dumped object"
                )

            if issubclass(dumped_object.__class__, BaseModel):
                request_data = dumped_object.model_dump_json(by_alias=True)
            elif isinstance(dumped_object, dict):
                request_data = dumped_object
            else:
                raise ValueError(
                    "dumped_object must be a BaseModel, FikenObject or dict"
                )

        headers = {
            "Authorization": f"Bearer {token.access_token if isinstance(token, AccessToken) else token}",
            "User-Agent": "FikenPy/%s (Python %s)"
            % (version("fiken_py"), platform.python_version()),
            "Content-Type": "application/json",
        }

        headers = headers.copy()
        if file_data is not None:
            headers.pop("Content-Type")
        headers["X-Request-ID"] = str(uuid.uuid4())

        # TODO - tests for this
        timestamp_ms = time.time_ns() // 1000000
        if cls._RATE_LIMIT_ENABLED:
            if cls._REQUESTS_COUNTER >= cls._MAX_REQUESTS_PER_SECOND:
                time_diff = timestamp_ms - cls._LAST_REQUEST_TIME
                if time_diff < 1000:
                    sleep_time = 1000 - time_diff
                    logger.debug(
                        f"Sending requests too fast. Sleeping for {sleep_time} ms"
                    )
                    time.sleep(sleep_time / 1000)
                    cls._REQUESTS_COUNTER = 0
            cls._REQUESTS_COUNTER += 1
            cls._LAST_REQUEST_TIME = timestamp_ms

        if file_data is not None:
            request_data = None  # Only send the file if it is a file request

        headers_debug = headers.copy()
        headers_debug["Authorization"] = "Bearer [REDACTED]"
        logger.debug(
            f"""Executing {method_name} on {cls.__name__} at {url}
        params: {kwargs}
        headers: {headers_debug}
        data: {request_data}"""
        )

        try:
            response = requests.request(
                method_name,
                url,
                headers=headers,
                params=kwargs,
                data=request_data,
                files=file_data,
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Request connection failed: {e}")
            raise RequestConnectionException(e)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if (
                e.response.status_code == 403 and trial == 0
            ):  # For 403 error - try refreshing token once
                if isinstance(token, AccessToken):
                    try:
                        token.attempt_refresh()
                        return cls._execute_method(
                            method,
                            url,
                            dumped_object,
                            file_data,
                            token,
                            trial + 1,
                            **kwargs,
                        )
                    except RequestErrorException as err:
                        logger.error(f"Failed to refresh token: {err}")
                        raise

            handle_error(e)
            raise

        return response

    @property
    def is_new(self) -> bool:
        """
        Returns whether the object is new or not.
        :return: True if new, False if not, None if not applicable to object
        """
        return self.id_attr[1] is None

    @property
    def is_auth_token_local(self) -> bool:
        return (self._AUTH_TOKEN is not None) and (FikenObject._AUTH_TOKEN is None)

    @property
    def _auth_token(self) -> AccessToken | str | None:
        """Get either the local or global auth token."""
        return self._AUTH_TOKEN

    @property
    def _company_slug(self) -> str | None:
        """Gets either the local or global company slug."""
        return self._COMPANY_SLUG

    @classmethod
    def _inject_token_and_slug_and_return(
        cls,
        obj: typing.Self,
        token: OptionalAccessToken,
        company_slug: Optional[str] = None,
    ) -> typing.Self:
        """Injects the token and company slug into the object and returns it.
        Takes first the local token and company slug, then the global ones.
        """
        obj._AUTH_TOKEN = token
        obj._COMPANY_SLUG = company_slug

        return obj


class FikenObjectRequiringRequest(FikenObject):

    @abc.abstractmethod
    def _to_request_object(self, **kwargs) -> BaseModel:
        """Converts the object to a request object"""

        raise NotImplementedError("Method not implemented")

    @staticmethod
    def _pack_common_fields(
        base_object: BaseModel, request_object_type: type[BaseModel]
    ) -> dict:
        """Returns the common field and values between the base and request objects"""

        common_fields = {}
        for base_field in request_object_type.model_fields:
            if base_field in base_object.__class__.model_fields:
                common_fields[base_field] = getattr(base_object, base_field)
            else:
                logger.warning(
                    f"Field {base_field} not present in {base_object.__class__.__name__}"
                )
        return common_fields


class FikenObjectAttachable(FikenObject):
    _extension_to_mime_map = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "ico": "image/x-icon",
        "svg": "image/svg+xml",
        "svgz": "image/svg+xml",
        "tiff": "image/tiff",
        "tif": "image/tiff",
        "ai": "application/postscript",
        "drw": "application/drafting",
        "pct": "image/pict",
        "psp": "image/x-paintshoppro",
        "webp": "image/webp",
        "heic": "image/heic",
        "raw": "image/raw",
    }

    @classmethod  # TODO - some kind of @classproperty ?
    def _attachment_url(cls):
        return cls._get_method_base_URL(RequestMethod.GET) + "/attachments"

    @classmethod
    def _extract_extension(cls, filename: str) -> str:
        if "." not in filename:
            raise ValueError("Filename must have an extension.")
        return filename.split(".")[-1]

    @classmethod
    def _extension_to_mime(cls, extension: str) -> str:
        if extension in cls._extension_to_mime_map:
            return cls._extension_to_mime_map[extension]
        else:
            raise ValueError(f"Unsupported file extension {extension}")

    @classmethod
    def get_attachments_cls(
        cls,
        instance: Optional[typing.Self] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ) -> list[Attachment]:
        url = cls._attachment_url()

        if token is None and instance is not None:
            token = instance._auth_token

        if instance is not None:
            if (
                kwargs.get(instance.id_attr[0]) is None
                and instance.id_attr[1] is not None
            ):
                kwargs[instance.id_attr[0]] = instance.id_attr[1]

        try:
            response = cls._execute_method(
                RequestMethod.GET, url, token=token, **kwargs
            )
        except RequestErrorException:
            raise

        data = response.json()

        return [Attachment(**item) for item in data]

    def get_attachments(
        self, token: OptionalAccessToken = None, **kwargs
    ) -> list[Attachment]:
        """Gets all attachments for the resource."""
        return self.__class__.get_attachments_cls(self, token=token, **kwargs)

    @classmethod
    def add_attachment_bytes_cls(
        cls,
        filename: str,
        data: bytes,
        comment: Optional[str] = None,
        instance: Optional[typing.Self] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        """Adds an attachment in form of bytes."""
        if filename is None or data is None:
            raise ValueError("Filename and/or data must be provided")

        if " " in filename:
            raise ValueError("Filename must not contain spaces")

        try:
            extension = cls._extract_extension(filename)
            extension_mime = cls._extension_to_mime(extension)
        except ValueError:
            raise

        sent_data = {
            "file": (filename, data, extension_mime),
            "filename": (None, filename),
            "comment": (None, comment),
        }

        try:
            response = cls._execute_method(
                RequestMethod.POST,
                url=cls._attachment_url(),
                dumped_object=instance,
                file_data=sent_data,
                token=token,
                **kwargs,
            )
        except RequestErrorException:
            raise

        if response.status_code != 201:
            return False
        return True

    @classmethod
    def add_attachment_cls(
        cls,
        filepath,
        filename: Optional[str] = None,
        comment: Optional[str] = None,
        instance: Optional[typing.Self] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        """Adds an attachment."""
        if filepath is None:
            raise ValueError("A path to the attachment must be provided")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} does not exist")

        with open(filepath, "rb") as f:
            file_data = f.read()

        if filename is None:
            filename = filepath.split("/")[-1]

        return cls.add_attachment_bytes_cls(
            filename, file_data, comment, instance, token=token, **kwargs
        )

    def add_attachment(
        self,
        filepath,
        filename: Optional[str] = None,
        comment: Optional[str] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        if token is None:
            token = self._auth_token
        return self.add_attachment_cls(
            filepath, filename, comment, instance=self, token=token, **kwargs
        )

    def add_attachment_bytes(
        self,
        filename: str,
        data: bytes,
        comment: Optional[str] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        if token is None:
            token = self._auth_token
        return self.add_attachment_bytes_cls(
            filename, data, comment, instance=self, token=token, **kwargs
        )


class FikenObjectCountable(FikenObject):

    @classmethod
    def get_counter(cls, token: OptionalAccessToken = None, **kwargs) -> int:
        url = cls._get_method_base_URL("COUNTER")

        try:
            response = cls._execute_method(
                RequestMethod.GET, url, token=token, **kwargs
            )
        except RequestErrorException:
            raise

        try:
            return Counter(**response.json()).value
        except ValidationError:
            raise

    @classmethod
    def set_initial_counter(
        cls, counter: int, token: OptionalAccessToken | None = None, **kwargs
    ) -> bool:
        """Set the default invoice counter to the given value
        :param token: Token to use for the request
        :param counter: The value to set the counter to
        :return: True if the counter was set successfully, False otherwise"""
        url = cls._get_method_base_URL("COUNTER")

        counter_obj = Counter(value=counter)

        try:
            response = cls._execute_method(
                RequestMethod.POST,
                url,
                token=token,
                dumped_object=counter_obj,
                **kwargs,
            )
        except RequestErrorException:
            raise

        if response.status_code != 201:
            return False
        return True


class FikenObjectDeleteFlagable(FikenObject):
    """Base class for FikenObjects who are deleted by creating a counter-entry and setting a deleted-flag to True"""

    def delete(
        self,
        description: Optional[str] = None,
        token: OptionalAccessToken = None,
        **kwargs,
    ):
        """
        Does not delete the object itself, but creates a counter-entry and sets the deleted flag to True.
        :arg description: The description of the deletion
        :return: None
        """

        if description is None:
            raise ValueError("Description must be provided")

        kwargs["description"] = description

        if token is None:
            token = self._auth_token

        if kwargs.get("companySlug") is None:
            kwargs["companySlug"] = self._company_slug

        try:
            self._execute_method(
                RequestMethod.PATCH,
                url=self._get_method_base_URL(RequestMethod.DELETE),
                token=token,
                dumped_object=self,
                **kwargs,
            )
            self._refresh_object(**kwargs)
        except RequestErrorException as e:
            raise


class FikenObjectPaymentable(FikenObject):

    def add_payment(
        self, payment: "Payment", token: OptionalAccessToken = None, **kwargs
    ) -> "Payment":
        """Adds a payment to the object"""

        if kwargs.get(self.id_attr[0]) is None:
            kwargs[self.id_attr[0]] = self.id_attr[1]

        if token is None:
            token = self._auth_token

        if kwargs.get("companySlug") is None:
            kwargs["companySlug"] = self._company_slug

        return payment.save(token=token, **kwargs)
