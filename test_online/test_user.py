from fiken_py.models import UserInfo


def test_get_user_info():
    user: UserInfo = UserInfo.get()

    assert user is not None
    assert user.name is not None
    assert user.email is not None