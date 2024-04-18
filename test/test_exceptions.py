import pytest
from fiken_py.fiken_object import FikenObject


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


# def test_get_path_single_not_supported():
#     class TestObject(FikenObject):
#         _GET_PATH_SINGLE = None
#
#     with pytest.raises(NotImplementedError) as e:
#         TestObject.get()
#     assert str(e.value) == "Method not implemented"
#
#
#
# def test_get_path_multiple_not_supported():
#     class TestObject(FikenObject):
#         _GET_PATH_MULTIPLE = None
#
#     with pytest.raises(NotImplementedError) as e:
#         TestObject.getAll()
#     assert str(e.value) == "Method not implemented"
#
#
#
# def test_post_path_not_supported():
#     class TestObject(FikenObject):
#         _POST_PATH = None
#
#     with pytest.raises(NotImplementedError) as e:
#         TestObject().save()
#     assert str(e.value) == "Method not implemented"
#
#
# def test_delete_path_not_supported():
#     class TestObject(FikenObject):
#         _DELETE_PATH = None
#
#     with pytest.raises(NotImplementedError) as e:
#         TestObject().delete()
#     assert str(e.value) == "Method not implemented"