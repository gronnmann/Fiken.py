from typing import Optional

import pytest
import requests_mock
from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, RequestMethod


def test_auth_token_not_set():
    with pytest.raises(ValueError) as e:
        FikenObject.get()
    assert str(e.value) == "Auth token not set"

    with pytest.raises(ValueError) as e:
        FikenObject.getAll()
    assert str(e.value) == "Auth token not set"

    # test save and delete
    object = FikenObject()
    with pytest.raises(ValueError) as e:
        object.save()
    assert str(e.value) == "Auth token not set"

    with pytest.raises(ValueError) as e:
        object.delete()
    assert str(e.value) == "Auth token not set"


def test_get_method_base_url():
    class TestObject(FikenObject, BaseModel):
        _GET_PATH_SINGLE = '/companies/{companySlug}/test/{testId}'
        _GET_PATH_MULTIPLE = '/companies/{companySlug}/tests/'
        _POST_PATH = '/companies/{companySlug}/tests/'
        _PUT_PATH = '/companies/{companySlug}/test/{testId}'

    base_url = FikenObject.PATH_BASE

    assert TestObject._get_method_base_URL(RequestMethod.GET) == base_url + '/companies/{companySlug}/test/{testId}'
    assert TestObject._get_method_base_URL(RequestMethod.GET_MULTIPLE) == base_url + '/companies/{companySlug}/tests/'
    assert TestObject._get_method_base_URL(RequestMethod.POST) == base_url + '/companies/{companySlug}/tests/'
    assert TestObject._get_method_base_URL(RequestMethod.PUT) == base_url + '/companies/{companySlug}/test/{testId}'


def test_PUT_and_POST():
    class TestObject(BaseModel, FikenObject):
        _POST_PATH = '/companies/tests/'
        _PUT_PATH = '/companies/tests/{testId}'
        _GET_PATH_SINGLE = '/companies/tests/{testId}'
        testId: Optional[int] = None
        testName: Optional[str] = None

        @property
        def is_new(self):
            return self.testId is None

    url_get = TestObject._get_method_base_URL(RequestMethod.GET)
    url_get = url_get.replace("{testId}", "1")

    url_post = TestObject._get_method_base_URL(RequestMethod.POST)
    url_put = TestObject._get_method_base_URL(RequestMethod.PUT)
    url_put = url_put.replace("{testId}", "1")

    with requests_mock.Mocker() as m:
        FikenObject.set_auth_token("SAMPLE_TOKEN")

        m.get(url_get, json={
            'testId': 1
        })
        m.get(url_get + "/v2", json={
            'testId': 1,
            'testName': 'Test'
        })

        m.post(url_post, json={}, headers={'Location': url_get})
        m.put(url_put, json={}, headers={'Location': url_get + "/v2"})

        obj = TestObject()
        obj.save()
        assert obj.testId is 1
        assert obj.testName is None

        obj.testName = "Test"
        obj.save()

        assert obj.testId == 1
        assert obj.testName == 'Test'
