from aiohttp import web

import asynctest

from ..testing import HandlerTestCase
from ..middleware import (
    BaseBasicAuthMiddlewareFactory,
    BasicAuthMiddlewareFactory,
)


class SampleBasicAuthMiddlewareFactory(BaseBasicAuthMiddlewareFactory):

    def __init__(self, realm):
        super().__init__(realm)
        self.calls = []

    async def is_valid_auth(self, user, password):
        self.calls.append((user, password))
        return (user, password) == ('user', 'pass')


class SampleCollection:

    def __init__(self):
        self.calls = []

    async def credentials_match(self, user, password):
        self.calls.append((user, password))
        return (user, password) == ('user', 'pass')


class BaseBasicAuthMiddlewareFactoryTest(HandlerTestCase):

    def setUp(self):
        self.middleware = SampleBasicAuthMiddlewareFactory('realm')
        super().setUp()

    def create_app(self):
        return web.Application(middlewares=[self.middleware])

    async def test_is_valid_auth_default(self):
        """By default is_valid_auth returns False."""
        middleware = BaseBasicAuthMiddlewareFactory('realm')
        self.assertFalse(await middleware.is_valid_auth('user', 'pass'))

    async def test_no_auth_set(self):
        """If no authentication is set, Unauthorized is returned."""
        calls = []

        async def handler(request):
            calls.append(request)
            return web.HTTPOk()

        middleware_handler = await self.middleware(self.app, handler)
        request = self.get_request()
        response = await middleware_handler(request)
        self.assertEqual(401, response.status)
        self.assertEqual(
            'Basic realm="realm"', response.headers['Www-Authenticate'])
        # the handler is not called
        self.assertEqual([], calls)
        self.assertEqual([], self.middleware.calls)

    async def test_invalid_auth(self):
        """If invalid auth details are provided, Unauthorized is returned."""
        calls = []

        async def handler(request):
            calls.append(request)
            return web.HTTPOk()

        middleware_handler = await self.middleware(self.app, handler)
        request = self.get_request(auth=('foo', 'bar'))
        response = await middleware_handler(request)
        self.assertEqual(401, response.status)
        # the handler is not called
        self.assertEqual([], calls)
        # authentication is checked
        self.assertEqual([('foo', 'bar')], self.middleware.calls)

    async def test_valid_auth(self):
        """If auth is correctly provided, the handler is called."""
        calls = []

        async def handler(request):
            calls.append(request)
            return web.HTTPOk()

        middleware_handler = await self.middleware(self.app, handler)
        request = self.get_request(auth=('user', 'pass'))
        response = await middleware_handler(request)
        self.assertEqual(200, response.status)
        # the handler is called
        self.assertEqual([request], calls)
        # authentication is checked
        self.assertEqual([('user', 'pass')], self.middleware.calls)


class BasicAuthMiddlewareFactoryTest(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        self.calls = []

        async def checker(user, password):
            self.calls.append((user, password))
            return (user, password) == ('user', 'pass')

        self.middleware = BasicAuthMiddlewareFactory('realm', checker)

    async def test_validate_credentials_true(self):
        """is_valid_auth returns True if the credentials check passes."""
        self.assertTrue(await self.middleware.is_valid_auth('user', 'pass'))
        self.assertEqual([('user', 'pass')], self.calls)

    async def test_validate_credentials_false(self):
        """is_valid_auth returns False if the credentials check fails."""
        self.assertFalse(await self.middleware.is_valid_auth('foo', 'bar'))
        self.assertEqual([('foo', 'bar')], self.calls)
