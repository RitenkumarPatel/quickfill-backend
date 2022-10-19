from __future__ import annotations

from typing import Optional, Iterable

from flask import Response


def response(
    status: int,  # HTTPStatus
    description: Optional[str] = "",
    error: Optional[str] = "",
    content: Optional[dict] = None,
) -> Iterable[str] | Iterable[bytes]:
    """Builds a dictionary containing certain details about an API call.

    :param status: The HTTP status code that is the result of the API call.
    :param description: An optional description of what occurred as a result of
        making the API call.
    :param error: An optional description of an error that occurred as a result
        of making the API call.
    :param content: An optional dictionary object containing any returned data
        as a result of making the API called. A python dictionary should be
        passed into this optional parameter. The dictionary is later converted
        into a JSON object by flask.

    :return: The API response dictionary which is later converted into a JSON
        object by flask.
    """
    api_response = {"status": status}
    if description:
        api_response["description"] = description
    if error:
        api_response["error"] = error
    if content:
        api_response["content"] = content

    flask_response = Response(api_response)
    flask_response.headers["Allow-Control-Access-Origin"] = "*"

    return flask_response.response
