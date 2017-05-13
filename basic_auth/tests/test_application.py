from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)

from ..testing import basic_auth_header
from ..api.testing import APIApplicationTestCase
from ..middleware import BaseBasicAuthMiddlewareFactory
from ..application import (
    BasicAuthCheckApplication,
    setup_api_application,
    setup_auth_check_application
)
from ..collection import MemoryCredentialsCollection


class AuthCheckMiddlewareFactory(BaseBasicAuthMiddlewareFactory):

    def is_valid_auth(self, user, password):
        if (user, password) == ('user', 'pass'):
            return True
        return False


class BasicAuthCheckApplicationTest(AioHTTPTestCase):

    async def get_application(self):
        middleware = AuthCheckMiddlewareFactory('realm')
        return BasicAuthCheckApplication(middleware)

    @unittest_run_loop
    async def test_no_auth(self):
        """A request without auth set returns Unauthorized."""
        response = await self.client.request('GET', '/')
        self.assertEqual(401, response.status)

    @unittest_run_loop
    async def test_invalid_auth(self):
        """A request with invalid auth returns Unauthorized."""
        auth = basic_auth_header('foo', 'bar')
        response = await self.client.request('GET', '/', headers=auth)
        self.assertEqual(401, response.status)

    @unittest_run_loop
    async def test_valid_auth(self):
        """A request with valid auth returns OK."""
        auth = basic_auth_header('user', 'pass')
        response = await self.client.request('GET', '/', headers=auth)
        self.assertEqual(200, response.status)


class SetupAPIApplicationTest(APIApplicationTestCase):

    async def get_application(self):
        return setup_api_application(MemoryCredentialsCollection())

    @unittest_run_loop
    async def test_setup_api_application(self):
        """An application for the API is set up."""
        content = {"user": "foo", "token": "user:pass"}
        response = await self.client_request(
            method='POST', path='/credentials', json=content)
        self.assertEqual(content, await response.json())


class SetupAuthCheckApplicationTest(AioHTTPTestCase):

    async def get_application(self):
        return setup_auth_check_application(MemoryCredentialsCollection())

    @unittest_run_loop
    async def test_setup_auth_check_application(self):
        """An application for the Basic-Auth check is set up."""
        response = await self.client.request('GET', '/')
        self.assertEqual(401, response.status)
