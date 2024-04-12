from __future__ import annotations

import re
from typing import Any, TypeVar, ClassVar

import requests
import platform
from importlib.metadata import version

from fiken_py.errors import UnsupportedMethodException

T = TypeVar('T', bound='FikenObject')


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

    BASE_CLASS = None # For FikenObjectRequest and save not to give AttributeError

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
        if cls._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        # TODO - better way to do this?
        if cls._GET_PATH_SINGLE.default is None:
            raise UnsupportedMethodException(f"Object {cls.__name__} does not support getting single object")
        print("headers", cls._HEADERS)
        url = f'{cls._PATH_BASE}{cls._GET_PATH_SINGLE.default}'
        url, kwargs = cls._extract_placeholders(url, **kwargs)

        response = requests.get(url, headers=cls._HEADERS, params=kwargs)

        print("---- GET ----")
        print(f"URL: {response.request.url}")
        print(f"BODY: {response.request.body}")
        print(f"HEADERS: {response.request.headers}")
        print("-------------")

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

        print("---- GET ----")
        print(f"URL: {response.request.url}")
        print(f"BODY: {response.request.body}")
        print(f"HEADERS: {response.request.headers}")
        print("-------------")

        response.raise_for_status()  # raise exception if the request failed
        data = response.json()

        print(f"get all {response}")

        return [cls(**item) for item in data]

    @classmethod
    def _getFromURL(cls, url: str) -> T:
        response = requests.get(url, headers=cls._HEADERS)

        print("---- GET FROM URL ----")
        print(f"URL: {response.request.url}")
        print(f"BODY: {response.request.body}")
        print(f"HEADERS: {response.request.headers}")
        print(f"RESPONSE CONTENT: {response.content}")
        print("-------------")

        response.raise_for_status()

        data = response.json()
        return cls(**data)

    def save(self, **kwargs: Any) -> T|None:
        """
        Saves the object to the server.
        :param kwargs: arguments to replace placeholders in the path
        :return: None or the new object
        """
        # TODO - difference between post and put
        # TODO - maybe somehow check if object has id?
        if self.__class__._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        if self.__class__._POST_PATH.default is None:
            raise UnsupportedMethodException(f"Object {self.__class__.__name__} does not support saving")

        url = f'{self.__class__._PATH_BASE}{self.__class__._POST_PATH.default}'

        url, kwargs = self.__class__._extract_placeholders(url, **kwargs)

        # POST class using pydantic model dump
        response = requests.post(url, headers=self.__class__._HEADERS, data=self.json(),
                                 params=kwargs)

        print("---- POST ----")
        print(f"URL: {response.request.url}")
        print(f"BODY: {response.request.body}")
        print(f"HEADERS: {response.request.headers}")
        print(f"DATA: {self.json()}")
        print(f"RESPONSE CONTENT: {response.content}")
        print(f"RESPONSE HEADERS: {response.headers}")
        print(f"STATUS CODE: {response.status_code}")
        if response.headers.get("Location"):
            print(f"New resource location: {response.headers['Location']}")

        print("-------------")

        response.raise_for_status()

        # Should give location of new object
        location = response.headers.get("Location")
        if location:
            print(self.__class__)
            base_class = self.__class__.BASE_CLASS if issubclass(self.__class__, FikenObjectRequest) else self.__class__
            new_object = base_class._getFromURL(location)

            if base_class == self.__class__:
                # Override the current object with the new one
                self.__dict__.update(new_object.__dict__)
                return self
            return new_object

        return None

    def delete(self, **kwargs: Any) -> bool:
        print("DELETE")
        if self.__class__._AUTH_TOKEN is None:
            raise ValueError("Auth token not set")

        if self.__class__._DELETE_PATH.default is None:
            raise UnsupportedMethodException(f"Object {self.__class__.__name__} does not support saving")

        url = f'{self.__class__._PATH_BASE}{self.__class__._DELETE_PATH.default}'

        url = self._preprocess_placeholders(url)
        url, kwargs = self.__class__._extract_placeholders(url, **kwargs)

        # POST class using pydantic model dump
        response = requests.delete(url, headers=self.__class__._HEADERS,
                                 params=kwargs)

        print("---- DELETE ----")
        print(f"URL: {response.request.url}")
        print(f"BODY: {response.request.body}")
        print(f"HEADERS: {response.request.headers}")
        print(f"RESPONSE CONTENT: {response.content}")
        print(f"RESPONSE HEADERS: {response.headers}")
        print(f"STATUS CODE: {response.status_code}")

        print("-------------")

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
                print("placeholder", placeholder)
                print("Path before: ", path)
                path = path.replace(f"{{{placeholder}}}", str(getattr(self, placeholder)))
                print("Path after: ", path)

        return path

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

    def save(self, **kwargs: Any) -> T|None:
        if self.__class__.BASE_CLASS is None:
            raise ValueError("BASE_CLASS not set")

        return super().save(**kwargs)