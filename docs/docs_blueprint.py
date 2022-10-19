import os.path
import pathlib

# noinspection PyPackageRequirements
import google
import cachecontrol
from http import HTTPStatus
from flask import Blueprint, session, redirect, request, abort
from flask_cors import cross_origin

# noinspection PyPackageRequirements
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import requests

from constants import *
from response import response

docs = Blueprint("docs", __name__)

# Bypass https requirement for OAuth 2. For development only.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secrets.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=GOOGLE_API_SCOPES,
    redirect_uri=f"{DOMAIN}/api/docs/callback",
)


def auth_required(func):

    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return response(HTTPStatus.UNAUTHORIZED,
                            error="The user is not logged in.")
        else:
            return func()

    wrapper.__name__ = func.__name__
    return wrapper


@docs.route(f"/api/docs/auth")
@cross_origin()
def auth():
    auth_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(auth_url)


@docs.route(f"/api/docs/unauth")
def unauth():
    session.clear()
    return response(HTTPStatus.OK, description="The user logged out.")


@docs.route(f"/api/docs/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # Mismatched state

    cached_session = cachecontrol.CacheControl(requests.session())
    token_request = google.auth.transport.requests.Request(
        session=cached_session)
    # noinspection PyProtectedMember
    id_info = id_token.verify_oauth2_token(
        id_token=flow.credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return response(HTTPStatus.OK,
                    description="The user logged in.",
                    content=dict(id_info))
