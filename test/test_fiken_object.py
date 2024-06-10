from typing import Optional

import pytest
import requests_mock
from pydantic import BaseModel

from fiken_py.fiken_object import FikenObject, RequestMethod


@pytest.fixture
def m():
    with requests_mock.Mocker() as m:
        yield m


def test_auth_token_not_set():
    class TestFikenObject(FikenObject):
        @property
        def id_attr(self):
            return "testId", None

    with pytest.raises(ValueError) as e:
        TestFikenObject.get()
    assert str(e.value) == "Auth token not set"

    with pytest.raises(ValueError) as e:
        TestFikenObject.getAll()
    assert str(e.value) == "Auth token not set"

    # test save and delete
    test_obj = TestFikenObject()
    with pytest.raises(ValueError) as e:
        test_obj.save()
    assert str(e.value) == "Auth token not set"

    with pytest.raises(ValueError) as e:
        test_obj.delete()
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


def test_get_all_pagination(m: requests_mock.Mocker):
    class TestObject(BaseModel, FikenObject):
        _GET_PATH_MULTIPLE = '/companies/tests/'
        testId: Optional[int] = None

    url = TestObject._get_method_base_URL(RequestMethod.GET_MULTIPLE)

    m.get(url, json=[
        {'testId': 1},
        {'testId': 2},
        {'testId': 3},
    ], headers={'Fiken-Api-Page-Count': '3'})

    m.get(url + "?page=1", json=[
        {'testId': 4},
        {'testId': 5},
    ])

    m.get(url + "?page=2", json=[
        {'testId': 6},
        {'testId': 7},
    ])

    m.get(url + "?page=3", json=
    [
        {'testId': 8},
        {'testId': 9},
        {'testId': 10},
    ])  # This shouldnt be included as Fiken-Api-Page-Count is 3

    objects = TestObject.getAll()
    assert len(objects) == 7
    assert objects[0].testId == 1
    assert objects[1].testId == 2
    assert objects[2].testId == 3
    assert objects[3].testId == 4
    assert objects[4].testId == 5
    assert objects[5].testId == 6
    assert objects[6].testId == 7

    objects_non_paged = TestObject.getAll(follow_pages=False)
    assert len(objects_non_paged) == 3
    assert objects_non_paged[0].testId == 1
    assert objects_non_paged[1].testId == 2
    assert objects_non_paged[2].testId == 3

    # removed page header
    m.get(url, json=[
        {'testId': 1},
        {'testId': 2},
        {'testId': 3},
    ])
    objects = TestObject.getAll()
    assert len(objects_non_paged) == 3
    assert objects[0].testId == 1
    assert objects[1].testId == 2
    assert objects[2].testId == 3
