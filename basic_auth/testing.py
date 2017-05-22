"""Testing utilities."""

import json

import yaml

import asynctest

from aiohttp import (
    web,
    BasicAuth,
    streams,
)
from aiohttp.helpers import sentinel
from aiohttp.test_utils import make_mocked_request

from .config import Config


TEST_DB_DSN = 'postgresql:///basic-auth-test'


def create_test_config(filename=None, use_db=True, db_dsn=TEST_DB_DSN,
                       port=8080):
    """Return a test configuration Config object.

    If filename is given, the configuration is also written to file.

    """
    config = {
        'db': {
            'dsn': db_dsn
        },
        'app': {
            'port': port
        }
    }
    if not use_db:
        config['app']['no-db'] = True

    if filename:
        with open(filename, 'w') as fd:
            yaml.dump(config, stream=fd)
    return Config(config)


def basic_auth_header(user, password):
    """Return a dict with the basic-auth header key and value."""
    return {'Authorization': BasicAuth(user, password).encode()}


def get_request(app, path='/', method='GET', content=None,
                auth=None, content_type=None, headers=None,
                json_encode=True):
    """Create a test request.

    The `auth` parameter for Basic-Authorization can be provided as tuple with
    (user, password).

    If `json_encode` is set to False, the content is not converted to JSON (in
    which case it should be bytes).

    """
    if headers is None:
        headers = {}
    if auth is not None:
        headers.update(basic_auth_header(*auth))

    if json_encode and content is None:
        content = {}

    if content is not None:
        payload = streams.StreamReader(loop=app.loop)
        if json_encode:
            data = json.dumps(content).encode('utf-8')
        else:
            data = content
        payload.feed_data(data)
        payload.feed_eof()
        headers.update(
            {'Content-Type': 'application/json',
             'Content-Length': str(len(data))})
    else:
        payload = sentinel

    if content_type is not None:
        headers['Content-Type'] = content_type

    return make_mocked_request(
        method, path, app=app, payload=payload, headers=headers)


class HandlerTestCase(asynctest.TestCase):
    """Test class for testing direct calls to HTTP handlers."""

    def setUp(self):
        super().setUp()
        self.app = self.create_app()

    def create_app(self):
        return web.Application()

    def get_request(self, *args, **kwargs):
        """Create a test request."""
        return get_request(self.app, *args, **kwargs)
