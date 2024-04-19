from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Any, TypeVar, ClassVar

import requests
import platform
from importlib.metadata import version

from fiken_py.errors import UnsupportedMethodException

T = TypeVar('T', bound='FikenObject')

logger = logging.getLogger("fiken_py")


class RequestMethod(Enum):
    GET = "GET",
    GET_MULTIPLE = "GET_MULTIPLE",
    POST = "POST",
    PUT = "PUT",
    DELETE = "DELETE",


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
    _PATH_BASE = 'https://api.fiken.no/api/v2'
    _AUTH_TOKEN = None

    _HEADERS = {}

    BASE_CLASS = None  # For FikenObjectRequest and save not to give AttributeError

    @classmethod
    def set_auth_token(cls, token):
        cls._AUTH_TOKEN = token

        cls._HEADERS = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'FikenPy/%s (Python %s)' % (version('fiken_py'), platform.python_version()),
            'Content-Type': 'application/json'
        }

    @classmethod
    def get(cls, **kwargs: Any) -> T:

        response = cls._execute_method(RequestMethod.GET, **kwargs)

        logger.debug(f"GETting single object for {cls.__name__}")

        response.raise_for_status()  # raise exception if the request failed
        data = response.json()
        return cls(**data)

    @classmethod
    def getAll(cls, **kwargs: Any) -> list[T]:
        if cls._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        if cls._GET_PATH_MULTIPLE.default is None:
            raise UnsupportedMethodException(f"Object {cls.__name__} does not support getting list")

        url = f'{cls._PATH_BASE}{cls._GET_PATH_MULTIPLE.default}'
        url, kwargs = cls._extract_placeholders(url, **kwargs)

        response = requests.get(url, headers=cls._HEADERS, params=kwargs)

        logger.debug(f"GETting many objects for {cls.__name__}")

        response.raise_for_status()  # raise exception if the request failed
        data = response.json()

        return [cls(**item) for item in data]

    @classmethod
    def _getFromURL(cls, url: str) -> T | list[T]:
        response = requests.get(url, headers=cls._HEADERS)

        logger.debug(f"GETting single object from URL {url}")

        response.raise_for_status()

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

        response = self._execute_method(used_method, instance=self, **kwargs)

        response.raise_for_status()

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

        response = self._execute_method(RequestMethod.DELETE, instance=self, **kwargs)

        response.raise_for_status()

        for attr in self.__dict__:
            setattr(self, attr, None)

        return True

    # TODO - better way to do this?
    _PLACEHOLDER_REGEX = re.compile(r'{(\w+)}')

    @classmethod
    def _extract_placeholders(cls, path: str, **kwargs: Any) -> tuple[str, dict[str, Any]]:
        """
        Extract placeholders from the path and replace them with the values in kwargs.
        :returns the formatted path, and the remaining kwargs
        """
        placeholders = cls._PLACEHOLDER_REGEX.findall(path)

        for placeholder in placeholders:
            if placeholder not in kwargs:
                raise ValueError(f"Missing placeholder value for {placeholder} in {path}")

        path = path.format(**{placeholder: kwargs.pop(placeholder) for placeholder in placeholders})
        return path, kwargs

    def _preprocess_placeholders(self, path):
        """
        Preprocess placeholders in the path.
        Replace them with the values from the object.
        :param path: URL
        :return: the formatted path
        """
        placeholders = self._PLACEHOLDER_REGEX.findall(path)

        for placeholder in placeholders:
            if not hasattr(self, placeholder):
                continue
            else:
                path = path.replace(f"{{{placeholder}}}", str(getattr(self, placeholder)))

        return path

    @classmethod
    def _get_method_base_URL(cls, method: RequestMethod) -> None | str:
        """Gets the base URL corresponding to the method.
        If the method is unsupported, returns None"""

        if method == RequestMethod.GET:
            attr_name = f"_GET_PATH_SINGLE"
        elif method == RequestMethod.GET_MULTIPLE:
            attr_name = f"_GET_PATH_MULTIPLE"
        else:
            attr_name = f"_{method.name}_PATH"

        if hasattr(cls, attr_name):
            return f"{cls._PATH_BASE}{getattr(cls, attr_name).default}"
        return None

    @classmethod
    def _execute_method(cls, method: RequestMethod, url: str = None, instance: FikenObject = None,
                        **kwargs: Any) -> requests.Response:
        """Executes a method on the object
        :method: RequestMethod - the method to execute
        :url: str - the URL to execute the method on. If None, will be generated from the method
        :instance: FikenObject - the instance to execute the method on. If None, will be ignored
        :kwargs: dict - the arguments to pass to the method
        """

        if cls._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        if url is None:
            url = cls._get_method_base_URL(method)

        if url is None:
            raise UnsupportedMethodException(f"Object {cls.__name__} does not support {method.name}")

        if instance is not None:
            url = instance._preprocess_placeholders(url)

        url, kwargs = cls._extract_placeholders(url, **kwargs)

        method_name = method.name
        if method == RequestMethod.GET_MULTIPLE:
            method_name = "GET"

        request_data = None
        if method in [RequestMethod.POST, RequestMethod.PUT]:
            request_data = instance.model_dump_json(by_alias=True)

        logging.debug(f"""Executing {method_name} on {cls.__name__} at {url}
        params: {kwargs}
        headers: {cls._HEADERS}
        data: {request_data}""")

        response = requests.request(method_name, url, headers=cls._HEADERS, params=kwargs, data=request_data)

        response.raise_for_status()

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
        raise UnsupportedMethodException("Request objects can not be fetched")

    @classmethod
    def getAll(**kwargs):
        raise UnsupportedMethodException("Request objects can not be fetched")

    def save(self, **kwargs: Any) -> T | None:
        if self.__class__.BASE_CLASS is None:
            raise ValueError("BASE_CLASS not set")

        return super().save(**kwargs)
