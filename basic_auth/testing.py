"""Testing utilities."""

import json

import asynctest

from aiohttp import (
    web,
    BasicAuth,
    streams,
)
from aiohttp.helpers import sentinel
from aiohttp.test_utils import make_mocked_request


class HandlerTestCase(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        self.app = self.create_app()

    def create_app(self):
        return web.Application()

    def get_request(self, path='/', method='GET', content=None, auth=None,
                    headers=None):
        """Create a test request.

        The auth parameter for basic-auth can be provided as tuple with (user,
        pass).

        """
        if headers is None:
            headers = {}
        if auth is not None:
            headers['Authorization'] = BasicAuth(*auth).encode()

        if content is not None:
            payload = streams.StreamReader(loop=self.loop)
            payload.feed_data(json.dumps(content))
            payload.feed_eof()
            headers['Content-Type'] = 'application/json'
        else:
            payload = sentinel

        return make_mocked_request(
            method, path, app=self.app, payload=payload, headers=headers)
