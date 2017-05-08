import unittest

from aiohttp import web

import asynctest

from ..testing import HandlerTestCase
from ..middleware import (
    BaseBasicAuthMiddlewareFactory,
    basic_auth_realm,
)


class SampleBasicAuthMiddlewareFactory(BaseBasicAuthMiddlewareFactory):

    def __init__(self):
        self.calls = []

    def is_valid_auth(self, realm, user, password):
        self.calls.append((realm, user, password))
        return (user, password) == ('user', 'pass')


class BaseBasicAuthMiddlewareFactoryTest(HandlerTestCase):

    def setUp(self):
        self.middleware = SampleBasicAuthMiddlewareFactory()
        super().setUp()

    def create_app(self):
        return web.Application(middlewares=[self.middleware])

    @asynctest.fail_on(unused_loop=False)
    def test_is_valid_auth_default(self):
        """By default is_valid_auth returns false."""
        middleware = BaseBasicAuthMiddlewareFactory()
        self.assertFalse(middleware.is_valid_auth('realm', 'user', 'pass'))

    async def test_no_auth_required(self):
        """If no basic auth is required, the handler is executed normally."""
        calls = []

        async def handler(request):
            calls.append(request)
            return web.HTTPOk()

        middleware_handler = await self.middleware(self.app, handler)
        request = self.get_request()
        response = await middleware_handler(request)
        self.assertEqual(200, response.status)
        self.assertEqual([request], calls)
        # auth is not checked in the middleware
        self.assertEqual([], self.middleware.calls)

    async def test_no_auth_set(self):
        """If auth is required but not set, Unauthorized is returned."""
        calls = []

        @basic_auth_realm('realm')
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

        @basic_auth_realm('realm')
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
        self.assertEqual([('realm', 'foo', 'bar')], self.middleware.calls)

    async def test_valid_auth(self):
        """If auth is correctly provided, the handler is called."""
        calls = []

        @basic_auth_realm('realm')
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
        self.assertEqual([('realm', 'user', 'pass')], self.middleware.calls)


class BasicAuthRealmTest(unittest.TestCase):

    def test_set_realm(self):
        """basic_auth_realm sets the realm attribute on the handler."""

        @basic_auth_realm('realm')
        def handler(request):
            pass

        self.assertEqual('realm', handler._basic_auth_realm)
