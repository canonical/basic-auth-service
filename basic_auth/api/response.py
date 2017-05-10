"""HTTP helpers."""

import json
from http import HTTPStatus

from aiohttp import web


_HTTP_STATUS_MAP = {status.value: status for status in HTTPStatus}


def APIResponse(content=None, response='Ok', **kwargs):
    """Return an API Response with the specified JSON-serializable content.

    The `response` parameter is the name of the `aiohttp` response class,
    without the "HTTP" prefix.

    Excess keyword arguments are passed to the response class.

    """
    if not content:
        content = {}
    cls = getattr(web, 'HTTP' + response)
    return cls(
        text=json.dumps(content), content_type='application/json', **kwargs)


def APIError(http_error, *args, message=None):
    """Return an API error for the specified HTTP error.

    This wraps `aiohttp.web_exception` errors to return JSON content type with
    a standard format for errors.

    `error_name` can be a string matching the error class name, without the
    "HTTP" prefix.

    """
    if isinstance(http_error, str):
        http_error = getattr(web, 'HTTP' + http_error)
    phrase = _HTTP_STATUS_MAP[http_error.status_code].phrase
    if message is None:
        message = phrase
    text = json.dumps({'code': phrase, 'message': message})
    return http_error(*args, content_type='application/json', text=text)
