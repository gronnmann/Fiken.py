from datetime import date
from random import random

import pytest
import requests_mock
import random

from pydantic import BaseModel

from fiken_py.fiken_types import CaseInsensitiveEnum
from sample_data_reader import get_sample_from_json

from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Account, BankAccount, Company, Contact, ContactPerson, Product, \
    ProductSalesReport, ProductSalesReportRequest, Transaction, JournalEntry, InboxDocument, Sale, Project, Invoice


@pytest.fixture(autouse=True)
def set_auth_token():
    FikenObject.set_auth_token("SAMPLE_TOKEN")


@pytest.fixture
def m():
    with requests_mock.Mocker() as m:
        yield m


@pytest.mark.parametrize("object", [
    UserInfo,
    Account,
    BankAccount,
    Company,
    Contact,
    ContactPerson,
    Product,
    ProductSalesReportRequest,
    ProductSalesReport,
    JournalEntry,
    Transaction,
    InboxDocument,
    Project,
    Sale,
    Invoice,
])
def test_object_methods(object: FikenObject, m: requests_mock.Mocker):
    print(f"---- TESTING {object.__name__} ----")

    if hasattr(object, '_GET_PATH_SINGLE') and object._GET_PATH_SINGLE.default is not None:
        print("Testing GET one")
        get_one(object, m)

    if hasattr(object, '_GET_PATH_MULTIPLE') and object._GET_PATH_MULTIPLE.default is not None:
        print("Testing GET multiple")
        get_multiple(object, m)

    print("-----------------------------------")


def get_one(object: FikenObject, m: requests_mock.Mocker):
    sample_data_path = _class_to_snake_case(object)
    sample_data = get_sample_from_json(sample_data_path)

    url = _url_get_one(object)
    kwargs, url = _generate_kwargs_and_url(object, url)

    m.get(url, json=sample_data)

    print(f"""Test: GET one
    URL: {url}
    Sample data: {sample_data}
    Sample data path: {sample_data_path}""")

    # check if no exception on get
    obj = object.get(**kwargs)
    assert obj is not None

    # check that all attributes from the sample data are in the object

    _compare_object_to_sample_data(obj, sample_data)

    print("-----------------------------------")


def get_multiple(object: FikenObject, m: requests_mock.Mocker):
    sample_data_path = _class_to_snake_case(object)
    sample_data = get_sample_from_json(sample_data_path)

    # encapsulate the sample data in a list random n times
    n = random.randint(3, 10)
    sample_data = [sample_data] * n

    url = _url_get_multiple(object)
    kwargs, url = _generate_kwargs_and_url(object, url)

    m.get(url, json=sample_data)

    print(f"""Test: GET multiple
    URL: {url}
    Sample data: {sample_data}
    Sample data path: {sample_data_path}
    n = {n}""")

    # check if no exception on get all
    objs = object.getAll(**kwargs)
    assert objs is not None
    assert len(objs) == n

    for obj in objs:
        # check that all attributes from the sample data are in the object
        _compare_object_to_sample_data(obj, sample_data[0])


def _class_to_snake_case(obj):
    """Converts a python class to snake case"""
    # For example, UserInfo to user_info

    return ''.join(['_' + i.lower() if i.isupper() else i for i in obj.__name__]).lstrip('_')


def _generate_kwargs_and_url(obj, url) -> tuple[dict, str]:
    """Generates a dictionary of kwargs for the object"""
    placeholders = FikenObject._PLACEHOLDER_REGEX.findall(url)

    kwargs = {}
    for placeholder in placeholders:
        kwargs[placeholder] = "_PLACEHOLDER_"

    return kwargs, url.format(**kwargs)


def _url_get_one(obj):
    return f"{FikenObject.PATH_BASE}{obj._GET_PATH_SINGLE.default}"


def _url_get_multiple(obj):
    return f"{FikenObject.PATH_BASE}{obj._GET_PATH_MULTIPLE.default}"


def _compare_object_to_sample_data(obj, sample_data):
    # loop through attributes in object
    for attr, val in obj.__dict__.items():
        if isinstance(val, BaseModel):
            # if the attribute is a model, compare the model to the sample data
            _compare_object_to_sample_data(val, sample_data[attr])

        elif isinstance(val, date):
            assert val.isoformat() == sample_data.get(attr)

        elif isinstance(val, CaseInsensitiveEnum):
            assert val == sample_data.get(attr).upper() # CaseInsensitiveEnum matches on upper

        elif isinstance(val, list) and all(isinstance(i, BaseModel) for i in val):
            for i, item in enumerate(val):
                _compare_object_to_sample_data(item, sample_data[attr][i])
        else:
            # if the attribute is not a model, check if the attribute is in the sample data

            if obj.model_fields[attr].default_factory is not None:
                assert attr in sample_data

            # check if the attribute is the same as the sample data
            assert val == sample_data.get(attr)
