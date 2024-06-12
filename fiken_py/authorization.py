import datetime
import email.utils
import uuid
from typing import Tuple, Optional

import requests
from pydantic import BaseModel
from requests import Request
from requests.auth import HTTPBasicAuth

from fiken_py.errors import RequestErrorException
from fiken_py.util import handle_error


class AccessToken(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
    request_timestamp: datetime.datetime

    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    def get_expiration_time(self) -> datetime.datetime:
        return self.request_timestamp + datetime.timedelta(seconds=self.expires_in)

    def is_expired(self) -> bool:
        return self.get_expiration_time() < datetime.datetime.now(datetime.timezone.utc)

    def attempt_refresh(self):
        if self.client_id is None or self.client_secret is None:
            raise ValueError("Client id or secret not set")

        new_token = Authorization.get_access_token_refresh(
            self.client_id, self.client_secret, self.refresh_token
        )

        self.access_token = new_token.access_token
        self.refresh_token = new_token.refresh_token
        self.expires_in = new_token.expires_in


class Authorization:
    """
    Class for handling authorization with Fiken API
    The authorization is done with OAuth2

    The flow is as follows:
    1. Generate URL for authorization (generate_auth_url)
    1.1. User logs in and authorizes the application
    1.2. Redirect to the redirect_uri with a code

    2. Use the code to get an access and refresh token (get_access_token_authcode)
    2.1. The code is used to get an access token
    2.2. The access token is used to authenticate requests

    3. Set the access token for FikenObject.

    4. When the access token expires, use the refresh token to get a new access token (get_access_token_refresh)
    """

    _AUTHORIZATION_URL = "https://fiken.no/oauth/authorize"
    _TOKEN_ENDPOINT_URL = "https://fiken.no/oauth/token"

    @classmethod
    def generate_auth_url(
        cls, client_id: str, redirect_uri: str
    ) -> Tuple[str, uuid.UUID]:
        """
        Generates the URL for the authorization process.
        :param client_id: The client id provided by Fiken for the application
        :param redirect_uri: The redirect uri for the application
        :return: url and state (random UUID)
        """
        state = uuid.uuid4()

        auth_data = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }

        p = Request("GET", cls._AUTHORIZATION_URL, params=auth_data).prepare()
        return p.url, state

    @classmethod
    def _get_token_from_endpoint(
        cls, client_id: str, client_secret: str, data: dict
    ) -> AccessToken:

        basic_auth = HTTPBasicAuth(client_id, client_secret)

        response = requests.post(cls._TOKEN_ENDPOINT_URL, data=data, auth=basic_auth)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            handle_error(e)
            raise

        response_data = response.json()

        # get out response date
        date_header = response.headers.get("Date")
        date_parsed = None
        if date_header is not None:
            date_parsed = email.utils.parsedate_to_datetime(date_header)

        token = AccessToken(
            **response_data,
            request_timestamp=(
                date_parsed if date_header is not None else datetime.datetime.now()
            )
        )
        token.client_id = client_id
        token.client_secret = client_secret

        return token

    @classmethod
    def get_access_token_authcode(
        cls, client_id: str, client_secret: str, code: str, redirect_uri: str
    ) -> AccessToken:
        """
        Gets the access and refresh token from Fiken.
        :param client_id: The client id provided by Fiken for the application
        :param client_secret: The client secret provided by Fiken for the application
        :param code: The code received from the authorization process
        :param redirect_uri: The redirect uri for the application
        :return: access token and refresh token
        """

        data = {
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "state": uuid.uuid4(),
        }

        try:
            return cls._get_token_from_endpoint(client_id, client_secret, data)
        except RequestErrorException:
            raise

    @classmethod
    def get_access_token_refresh(
        cls, client_id: str, client_secret: str, refresh_token: str
    ) -> AccessToken:
        """
        Gets the access token from the refresh token.
        :param client_id: The client id provided by Fiken for the application
        :param client_secret: The client secret provided by Fiken for the application
        :param refresh_token: The refresh token received from the authorization process
        :return: access token and refresh token
        """

        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            return cls._get_token_from_endpoint(client_id, client_secret, data)
        except RequestErrorException:
            raise
