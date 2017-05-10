from unittest import TestCase
import json

from aiohttp import web

from ..response import (
    APIResponse,
    APIError,
)


class APIResponseTest(TestCase):

    def test_response(self):
        """APIResponse returns an HTTP response with JSON payload."""
        content = {'foo': 'bar'}
        response = APIResponse(content=content)
        self.assertEqual(200, response.status)
        self.assertEqual('application/json', response.content_type)
        self.assertEqual(content, json.loads(response.text))

    def test_response_type(self):
        """APIResponse can specify the response type."""
        response = APIResponse(content={}, response='Created')
        self.assertEqual(201, response.status)

    def test_response_extra_kwargs(self):
        """Extra keyword arguments can be passed to the response."""
        response = APIResponse(
            content={}, response='Created', headers={'Location': '/foo'})
        self.assertEqual(201, response.status)
        self.assertEqual('/foo', response.headers['Location'])

    def test_response_no_content(self):
        """If no content is passed, the response contains empty JSON."""
        response = APIResponse()
        self.assertEqual(200, response.status)
        self.assertEqual({}, json.loads(response.text))


class APIErrorTest(TestCase):

    def test_error(self):
        """APIError return an error response."""
        error = APIError(web.HTTPBadRequest)
        self.assertEqual(400, error.status)
        self.assertEqual('application/json', error.content_type)
        content = json.loads(error.text)
        self.assertEqual(
            {'code': 'Bad Request', 'message': 'Bad Request'}, content)

    def test_error_message(self):
        """APIError allows setting a custom message."""
        error = APIError(web.HTTPBadRequest, message='Request failed')
        content = json.loads(error.text)
        self.assertEqual(
            {'code': 'Bad Request', 'message': 'Request failed'}, content)

    def test_extra_params(self):
        """APIError passes parameters to the Error class."""
        error = APIError(
            web.HTTPMethodNotAllowed, 'POST', ('GET', 'PUT'))
        self.assertEqual('GET,PUT', error.headers['Allow'])

    def test_error_from_string(self):
        """The error class can be specified as string."""
        error = APIError('BadRequest')
        self.assertEqual(400, error.status)
