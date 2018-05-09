import os
import base64

from adal import AuthenticationContext
from flask import url_for

TENANT = os.environ['AZURE_CLIENT_TENANT']
CLIENT = os.environ['AZURE_CLIENT_ID']
SECRET = os.environ['AZURE_CLIENT_SECRET']
RESOURCE = os.environ['AZURE_CLIENT_RESOURCE']


def get_authorization_url(callback: str = '/') -> str:
    return f'https://login.microsoftonline.com/{TENANT}/oauth2/authorize?' \
           f'response_type=code&client_id={CLIENT}&' \
           f'redirect_uri={url_for("login_callback", _external=True)}&state={callback}&resource={RESOURCE}'


def get_random_str(length_in_bytes: int = 32) -> str:
    return base64.b64encode(os.urandom(length_in_bytes)).decode('utf-8')


def acquire_token(code: str):
    context = AuthenticationContext(f'https://login.microsoftonline.com/{TENANT}')
    return context.acquire_token_with_authorization_code(code, url_for("login_callback", _external=True), RESOURCE,
                                                         CLIENT, SECRET)


def get_logout_uri():
    return f'https://login.microsoftonline.com/{TENANT}/oauth2/logout'
