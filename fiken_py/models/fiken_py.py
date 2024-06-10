from typing import List

from fiken_py.authorization import AccessToken
from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Company


class FikenPy:
    """Class for interacting with the Fiken API using an OOP approach.
    Create this class after obtaining an access token, and then use its methods to interact with the API.
    """

    def __init__(self, auth_token: str | AccessToken):
        if FikenObject._AUTH_TOKEN is not None:
            raise ValueError("Global auth token already set (FikenObject.set_auth_token). "
                             "Please clear it before setting individual tokens.")

        self.access_token = auth_token

    def get_user_info(self) -> UserInfo:
        return UserInfo.get(token=self.access_token)

    def get_companies(self) -> List[Company]:
        return Company.getAll(token=self.access_token)

    def get_company(self, company_slug: str) -> Company:
        return Company.get(companySlug=company_slug, token=self.access_token)