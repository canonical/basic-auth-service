from aiohttp.test_utils import (
    AioHTTPTestCase,
    unittest_run_loop,
)

from ..credential import hash_token256
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

    async def is_valid_auth(self, user, password):
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

    CONTENT_TYPE = 'application/json;profile=basic-auth.api;version=1.0'

    async def get_application(self):
        collection = MemoryCredentialsCollection(loop=self.loop)
        return setup_api_application(collection)

    @unittest_run_loop
    async def test_setup_api_application(self):
        """An application for the API is set up."""
        content = {
            "user": "foo",
            "token": "user:pass"
        }
        expected = {
            "user": "foo",
            "token": "user:{}".format(hash_token256('pass'))
        }
        response = await self.client_request(
            method='POST', path='/credentials', json=content,
            content_type=self.CONTENT_TYPE,
            auth=('user', 'pass'))

        self.assertEqual(expected, await response.json())

    @unittest_run_loop
    async def test_basic_auth_required(self):
        """The API application requires basic auth."""
        content = {"user": "foo", "token": "user:pass"}
        response = await self.client_request(
            method='POST', path='/credentials', json=content,
            content_type=self.CONTENT_TYPE)
        self.assertEqual(401, response.status)


class SetupAuthCheckApplicationTest(AioHTTPTestCase):

    async def get_application(self):
        collection = MemoryCredentialsCollection(loop=self.loop)
        return setup_auth_check_application(collection)

    @unittest_run_loop
    async def test_setup_auth_check_application(self):
        """An application for the Basic-Auth check is set up."""
        response = await self.client.request('GET', '/')
        self.assertEqual(401, response.status)
