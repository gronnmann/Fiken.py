from __future__ import annotations

import logging
import os.path
import re
import time
import uuid
from enum import Enum
from typing import Any, TypeVar, ClassVar

import requests
import platform
from importlib.metadata import version

from pydantic import BaseModel

from fiken_py.errors import RequestWrongMediaTypeException, RequestConnectionException, RequestBadRequestException, \
    RequestUserUnauthenticatedException, RequestForbiddenException, RequestContentNotFoundException, \
    RequestUnsupportedMethodException, \
    RequestWrongMediaTypeException, RequestErrorException
from fiken_py.fiken_types import Attachment

T = TypeVar('T', bound='FikenObject')

logger = logging.getLogger("fiken_py")


class RequestMethod(Enum):
    GET = "GET",
    GET_MULTIPLE = "GET_MULTIPLE",
    POST = "POST",
    PUT = "PUT",
    DELETE = "DELETE",
    PATCH = "PATCH",


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
    PATH_BASE: ClassVar[str] = 'https://api.fiken.no/api/v2'
    _AUTH_TOKEN = None

    _HEADERS = {}
    _COMPANY_SLUG = None

    BASE_CLASS = None  # For FikenObjectRequest and save not to give AttributeError

    _RATE_LIMIT_ENABLED = True
    _MAX_REQUESTS_PER_SECOND = 4
    _REQUESTS_COUNTER = 0
    _LAST_REQUEST_TIME = 0

    @classmethod
    def set_auth_token(cls, token):
        cls._AUTH_TOKEN = token

        cls._HEADERS = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'FikenPy/%s (Python %s)' % (version('fiken_py'), platform.python_version()),
            'Content-Type': 'application/json'
        }

    @classmethod
    def set_company_slug(cls, company_slug):
        cls._COMPANY_SLUG = company_slug

    @classmethod
    def set_rate_limit(cls, enabled: bool):
        cls.RATE_LIMIT_ENABLED = enabled

    @classmethod
    def get(cls, **kwargs: Any) -> T | None:

        try:
            response = cls._execute_method(RequestMethod.GET, **kwargs)
        except RequestContentNotFoundException as e:
            return None
        except Exception as e:
            raise e

        logger.debug(f"GETting single object for {cls.__name__}")

        data = response.json()
        return cls(**data)

    @classmethod
    def getAll(cls, follow_pages: bool = True, **kwargs: Any) -> list[T]:

        logger.debug(f"GETting many objects for {cls.__name__}")
        try:
            response = cls._execute_method(RequestMethod.GET_MULTIPLE, **kwargs)
        except RequestErrorException as e:
            raise

        pages = [response.json()]
        if follow_pages:
            page_count = response.headers.get("Fiken-Api-Page-Count")
            if page_count is not None:
                page_count = int(page_count)
            if page_count is not None and page_count > 1:
                logger.debug(f"Multiple pages found. Fetching {page_count} pages")
                for i in range(1, page_count):
                    try:
                        response = cls._execute_method(RequestMethod.GET_MULTIPLE, page=i, **kwargs)
                    except RequestErrorException as e:
                        raise

                    pages.append(response.json())

        objects = []
        for page in pages:
            for item in page:
                objects.append(cls(**item))
        return objects

    @classmethod
    def _getFromURL(cls, url: str) -> T | list[T]:
        try:
            response = cls._execute_method(RequestMethod.GET, url=url)
        except RequestErrorException:
            raise

        logger.debug(f"GETting single object from URL {url}")

        data = response.json()

        return cls(**data)

    def save(self, **kwargs: Any) -> T | None:
        """
        Saves the object to the server.
        Checks if object is new or not and sends a POST or PUT request accordingly.
        If object has no method for checking if it is new, assumes POST.
        Throws an exception if object has PUT method defined, but no is new check.

        :param kwargs: arguments to replace placeholders in the path
        :return: None or the new object
        """

        if self._get_method_base_URL(RequestMethod.PUT) is not None:
            if self.is_new is None:
                raise NotImplementedError(
                    f"Object {self.__class__.__name__} has PUT path specified, but no is_new method")

        use_post = self.is_new if self.is_new is not None else True
        used_method = RequestMethod.POST if use_post else RequestMethod.PUT

        try:
            response = self._execute_method(used_method, dumped_object=self, **kwargs)
        except RequestErrorException:
            raise

        return self._follow_location_and_update_class(response)

    def _follow_location_and_update_class(self, response: requests.Response) -> None | T:
        """Follows the location header in the response and returns the new object.
        If new object is of the same class, updates the current object with the new one.
        """
        location = response.headers.get("Location")
        if location:
            logger.debug(f"Location of new object: {location}")

            base_class = self.__class__.BASE_CLASS if issubclass(self.__class__, FikenObjectRequest) else self.__class__
            new_object = base_class._getFromURL(location)

            if base_class == self.__class__:
                # Override the current object with the new one
                self.__dict__.update(new_object.__dict__)
                return self
            return new_object

        return None

    def delete(self, **kwargs: Any) -> bool:

        try:
            response = self._execute_method(RequestMethod.DELETE, dumped_object=self, **kwargs)
        except RequestErrorException:
            raise

        for attr in self.__dict__:
            setattr(self, attr, None)

        return True

    # TODO - better way to do this?
    _PLACEHOLDER_REGEX = re.compile(r'{(\w+)}')

    @classmethod
    def _extract_placeholders_kwargs(cls, path: str, **kwargs: Any) -> tuple[str, dict[str, Any]]:
        """
        Extract placeholders from the path and replace them with the values in kwargs.
        Also fills out companySlug if not provided.
        :returns the formatted path, and the remaining kwargs
        """

        if kwargs.get('companySlug') is None and cls._COMPANY_SLUG is not None:
            kwargs['companySlug'] = cls._COMPANY_SLUG

        placeholders = cls._PLACEHOLDER_REGEX.findall(path)

        for placeholder in placeholders:
            if placeholder not in kwargs:
                raise ValueError(f"Missing placeholder value for {placeholder} in {path}")

        path = path.format(**{placeholder: kwargs.pop(placeholder) for placeholder in placeholders})
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
                path = path.replace(f"{{{placeholder}}}", str(getattr(base_model, placeholder)))

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
            if type(method) == str:
                attr_name = f"_{method}_PATH"
            else:
                attr_name = f"_{method.name}_PATH"

        if hasattr(cls, attr_name):
            return f"{cls.PATH_BASE}{getattr(cls, attr_name).default}"
        return None

    @classmethod
    def _execute_method(cls, method: RequestMethod, url: str = None,
                        dumped_object: FikenObject | dict | BaseModel = None,
                        file_data: dict[str, tuple[Any | None, Any]] = None,
                        **kwargs: Any) -> requests.Response:
        """Executes a method on the object
        :method: RequestMethod - the method to execute
        :url: str - the URL to execute the method on. If None, will be generated from the method
        :dumped_object: - the object to send/dump and extract placeholders from. If None, will be ignored
        :kwargs: dict - the arguments to pass to the method
        """

        if cls._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        if file_data is not None and method != RequestMethod.POST:
            raise ValueError("Only POST requests can have file data")

        if file_data is not None and dumped_object is not None:
            raise ValueError("Only one of file data and instance can be provided")

        if url is None:
            url = cls._get_method_base_URL(method)

        if url is None:
            raise RequestWrongMediaTypeException(f"Object {cls.__name__} does not support {method.name}")

        if issubclass(dumped_object.__class__, BaseModel):
            url = cls._extract_placeholders_basemodel(url, dumped_object)

        url, kwargs = cls._extract_placeholders_kwargs(url, **kwargs)

        method_name = method.name
        if method == RequestMethod.GET_MULTIPLE:
            method_name = "GET"

        request_data = None
        if method in [RequestMethod.POST, RequestMethod.PUT, RequestMethod.PATCH]:
            if dumped_object is not None:
                if issubclass(dumped_object.__class__, BaseModel):
                    dumped_object: BaseModel
                    request_data = dumped_object.model_dump_json(by_alias=True)
                elif isinstance(dumped_object.__class__, dict):
                    request_data = dumped_object
                else:
                    raise ValueError("instance must be a BaseModel object or dict")

        headers = cls._HEADERS.copy()
        if file_data is not None:
            headers.pop("Content-Type")
        headers["X-Request-ID"] = str(uuid.uuid4())

        # TODO - tests for this
        timestamp_ms = time.time_ns() // 1000000
        if cls._RATE_LIMIT_ENABLED:
            if cls._REQUESTS_COUNTER >= cls._MAX_REQUESTS_PER_SECOND:
                time_diff = timestamp_ms - cls._LAST_REQUEST_TIME
                if time_diff < 1000:
                    sleep_time = (1000 - time_diff)
                    logger.debug(f"Sending requests too fast. Sleeping for {sleep_time} ms")
                    time.sleep(sleep_time / 1000)
                    cls._REQUESTS_COUNTER = 0
            cls._REQUESTS_COUNTER += 1
            cls._LAST_REQUEST_TIME = timestamp_ms

        logger.debug(f"""Executing {method_name} on {cls.__name__} at {url}
        params: {kwargs}
        headers: {cls._HEADERS}
        data: {request_data}""")

        try:
            response = requests.request(method_name, url, headers=headers, params=kwargs, data=request_data,
                                        files=file_data)
        except requests.exceptions.RequestException as e:
            logging.error(f"Request connection failed: {e}")
            raise RequestConnectionException(e)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"Request HTTP failed: {e}")
            if e.response.status_code == 400:
                raise RequestBadRequestException(e)
            elif e.response.status_code == 401:
                raise RequestUserUnauthenticatedException(e)
            elif e.response.status_code == 403:
                raise RequestForbiddenException(e)
            elif e.response.status_code == 404:
                raise RequestContentNotFoundException(e)
            elif e.response.status_code == 405:
                raise RequestUnsupportedMethodException(e)
            elif e.response.status_code == 415:
                raise RequestWrongMediaTypeException(e)
            else:
                raise RequestErrorException(e)

        return response

    @property
    def is_new(self) -> None | bool:
        """
        Returns whether the object is new or not.
        :return: True if new, False if not, None if not applicable to object
        """
        return None


class FikenObjectRequest(FikenObject):
    """
    Base class for all Fiken object requests.

    They only support save requests.
    They create their parent object when saved.
    """
    BASE_CLASS: ClassVar[FikenObject] = None

    @classmethod
    def get(**kwargs):
        raise RequestWrongMediaTypeException("Request objects can not be fetched")

    @classmethod
    def getAll(**kwargs):
        raise RequestWrongMediaTypeException("Request objects can not be fetched")

    def save(self, **kwargs: Any) -> T | None:
        if self.__class__.BASE_CLASS is None:
            raise ValueError("BASE_CLASS not set")

        return super().save(**kwargs)


class FikenObjectAttachable(FikenObject):

    @classmethod  # TODO - some kind of @classproperty ?
    def _attachment_url(cls):
        return cls._get_method_base_URL(RequestMethod.GET) + "/attachments"

    @classmethod
    def get_attachments_cls(cls, instance: FikenObjectAttachable = None, **kwargs) -> list[Attachment]:
        url = cls._attachment_url()

        try:
            response = cls._execute_method(RequestMethod.GET, url, instance, **kwargs)
        except RequestErrorException:
            raise

        data = response.json()

        return [Attachment(**item) for item in data]

    def get_attachments(self, **kwargs) -> list[Attachment]:
        """Gets all attachments for the resource.

        """
        return self.__class__.get_attachments_cls(self, **kwargs)

    @classmethod
    def add_attachment_bytes_cls(cls, filename: str, data: bytes, comment: str = None,
                                 instance: FikenObjectAttachable = None, **kwargs):
        """Adds an attachment in form of bytes."""
        if filename is None or data is None:
            raise ValueError("Filename and/or data must be provided")

        if '.' not in filename:
            raise ValueError("Filename must have an extension.")

        sent_data = {
            'file': (filename, data),
            'filename': (None, filename),
            'comment': (None, comment),
        }

        try:
            response = cls._execute_method(RequestMethod.POST,
                                           url=cls._attachment_url(), dumped_object=instance,
                                           file_data=sent_data, **kwargs)
        except RequestErrorException:
            raise

        if response.status_code != 201:
            return False
        return True

    @classmethod
    def add_attachment_cls(cls, filepath, filename: str = None, comment: str = None,
                           instance: FikenObjectAttachable = None, **kwargs):
        """Adds an attachment."""
        if filepath is None:
            raise ValueError("A path to the attachment must be provided")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} does not exist")

        with open(filepath, 'rb') as f:
            file_data = f.read()

        if filename is None:
            filename = filepath.split('/')[-1]

        return cls.add_attachment_bytes_cls(filename, file_data, comment, instance, **kwargs)

    def add_attachment(self, filepath, filename: str = None, comment: str = None, **kwargs):
        return self.add_attachment_cls(filepath, filename, comment, instance=self, **kwargs)

    def add_attachment_bytes(self, filename: str, data: bytes, comment: str = None, **kwargs):
        return self.add_attachment_bytes_cls(filename, data, comment, instance=self, **kwargs)
