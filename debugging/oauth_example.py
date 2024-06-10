import logging
import os

import dotenv
from fastapi import FastAPI, Request, Body, Query
from pydantic import BaseModel
from pyngrok import ngrok, conf

from fiken_py.authorization import Authorization, AccessToken
from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Company

dotenv.load_dotenv()

FIKEN_APP_ID = os.getenv("FIKEN_APP_ID")
FIKEN_APP_SECRET = os.getenv("FIKEN_APP_SECRET")
if FIKEN_APP_ID is None:
    print("FIKEN_APP_ID or FIKEN_APP_SECRET not found in environment variables.")
    exit(1)

logger = logging.getLogger("FikenPY OAuth2.0 Example")
logger.setLevel(logging.DEBUG)

# conf.get_default().config_path = "debugging/ngrok.yml"
# public_url = ngrok.connect(name="oauth_example")
# logger.info(f"Public URL: {public_url} -> http://localhost:8000")


app = FastAPI()

logger.info("test")


BASE_URL = "https://9c55-188-113-95-11.ngrok-free.app"

@app.get("/")
def read_root():
    return "This is a sample API for FikenPY showcasing the usage of OAuth2.0."


@app.get("/authorize")
def start_auth_process():
    url = Authorization.generate_auth_url(FIKEN_APP_ID, BASE_URL + "/auth_response")
    return {"url": url}


@app.get("/auth_response")
def auth_response(code: str = Query(...), state: str = Query(...)):

    token: AccessToken = Authorization.get_access_token_authcode(FIKEN_APP_ID, FIKEN_APP_SECRET,
                                                                 code,
                                                                 BASE_URL + "/auth_response")

    FikenObject.set_auth_token(token.access_token, (FIKEN_APP_ID, FIKEN_APP_SECRET))

    return Company.getAll()



@app.get("/refresh_token")
def refresh_token(refresh_token: str = Query(...)):
    token: AccessToken = Authorization.get_access_token_refresh(FIKEN_APP_ID, FIKEN_APP_SECRET, refresh_token)
    return {
        "token": token,
        "expires": token.get_expiration_time()
    }