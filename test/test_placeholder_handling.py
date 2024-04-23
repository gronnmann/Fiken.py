def test_extract_placeholders_kwargs_no_placeholders():
    path = "/api/v2/user"
    kwargs = {"id": 1}
    result = FikenObject._extract_placeholders_kwargs(path, **kwargs)
    assert result == (path, kwargs), "The path and kwargs should remain unchanged when there are no placeholders"


def test_extract_placeholders_kwargs_with_placeholders():
    path = "/api/v2/user/{id}"
    kwargs = {"id": 1}
    result = FikenObject._extract_placeholders_kwargs(path, **kwargs)
    assert result == (
        "/api/v2/user/1", {}), "The path should be formatted with the kwargs and the kwargs should be empty"


def test_extract_placeholders_kwargs_missing_placeholder():
    path = "/api/v2/user/{id}"
    kwargs = {}
    with pytest.raises(ValueError, match="Missing placeholder value for id in /api/v2/user/{id}"):
        FikenObject._extract_placeholders_kwargs(path, **kwargs)


def test_extract_placeholders_kwargs_multiple_placeholders():
    path = "/api/v2/user/{id}/post/{post_id}"
    kwargs = {"id": 1, "post_id": 2}
    result = FikenObject._extract_placeholders_kwargs(path, **kwargs)
    assert result == (
        "/api/v2/user/1/post/2", {}), "The path should be formatted with the kwargs and the kwargs should be empty"


import pytest
from fiken_py.fiken_object import FikenObject


def test_extract_placeholders_basemodel_no_placeholder():
    obj = FikenObject()
    obj.attribute = "value"
    path = "/api/v2/object"
    assert FikenObject._extract_placeholders_basemodel(path, obj) == path


def test_extract_placeholders_basemodel_with_placeholder():
    obj = FikenObject()
    obj.attribute = "value"
    path = "/api/v2/object/{attribute}"
    assert FikenObject._extract_placeholders_basemodel(path, obj) == "/api/v2/object/value"


def test_extract_placeholders_basemodel_with_nonexistent_placeholder():
    obj = FikenObject()
    obj.attribute = "value"
    path = "/api/v2/object/{nonexistent}"
    assert FikenObject._extract_placeholders_basemodel(path, obj) == path


def test_extract_placeholders_basemodel_with_multiple_placeholders():
    obj = FikenObject()
    obj.attribute1 = "value1"
    obj.attribute2 = "value2"
    path = "/api/v2/object/{attribute1}/{attribute2}"
    assert FikenObject._extract_placeholders_basemodel(path, obj) == "/api/v2/object/value1/value2"


def test_combined_no_placeholder():
    obj = FikenObject()
    obj.attribute = "value"
    path = "/api/v2/object"
    kwargs = {}
    preprocessed_path = FikenObject._extract_placeholders_basemodel(path, obj)
    result = FikenObject._extract_placeholders_kwargs(preprocessed_path, **kwargs)
    assert result == (path, kwargs)


def test_combined_with_placeholder_conflict():
    obj = FikenObject()
    obj.attribute = "value"
    path = "/api/v2/object/{attribute}"
    kwargs = {"attribute": "value2"}
    preprocessed_path = obj._extract_placeholders_basemodel(path, obj)
    result = FikenObject._extract_placeholders_kwargs(preprocessed_path, **kwargs)
    assert result == ("/api/v2/object/value", kwargs)


def test_combined_with_nonexistent_placeholder():
    obj = FikenObject()
    obj.attribute = "value"
    path = "/api/v2/object/{nonexistent}"
    kwargs = {}
    preprocessed_path = FikenObject._extract_placeholders_basemodel(path, obj)
    with pytest.raises(ValueError, match="Missing placeholder value for nonexistent in /api/v2/object/{nonexistent}"):
        FikenObject._extract_placeholders_kwargs(preprocessed_path, **kwargs)


def test_combined_with_multiple_placeholders_noconflict():
    obj = FikenObject()
    obj.attribute1 = "value1"
    path = "/api/v2/object/{attribute1}/{attribute2}"
    kwargs = {"attribute2": "value2"}
    preprocessed_path = FikenObject._extract_placeholders_basemodel(path, obj)
    result = FikenObject._extract_placeholders_kwargs(preprocessed_path, **kwargs)
    assert result == ("/api/v2/object/value1/value2", {})
