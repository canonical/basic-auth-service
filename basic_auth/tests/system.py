"""System tests."""

import subprocess
import os
import tempfile
import shutil
import time

import testresources

import asynctest

import aiohttp

from aiopg.sa import create_engine

from ..testing import create_test_config
from ..db.testing import ensure_database
from ..db import run_in_transaction


SYSTEM_TEST_DB_DSN = 'postgresql:///basic-auth-system-test'


class BasicAuthServiceResource(testresources.TestResourceManager):
    """A test resource running the service."""

    tempdir = None
    process = None

    def make(self, dep_resources):
        self.tempdir = tempfile.mkdtemp()
        config_file = os.path.join(self.tempdir, 'config.yaml')
        create_test_config(filename=config_file, db_dsn=SYSTEM_TEST_DB_DSN)

        self.process = subprocess.Popen(
            ['basic-auth', '--config', config_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # give time to the process to start
        return self

    def clean(self, resource):
        self.process.terminate()
        self.process.wait()
        # XXX include stdout/stderr in case of failure
        self.process.stdout.close()
        self.process.stderr.close()
        self.process = None
        shutil.rmtree(self.tempdir)
        self.tempdir = None


class SystemTests(asynctest.TestCase, testresources.ResourcedTestCase):

    resources = [('service', BasicAuthServiceResource())]

    async def setUp(self):
        super().setUp()
        self.client = aiohttp.ClientSession()
        ensure_database(dsn=SYSTEM_TEST_DB_DSN)
        # provide some api credentials for tests
        await self.call_model_method('add_api_credentials', 'user', 'pass')

    async def call_model_method(self, method, *args, **kwargs):
        """Call the specified Model method with arguments."""
        engine_context = create_engine(dsn=SYSTEM_TEST_DB_DSN, loop=self.loop)
        async with engine_context as engine:
            return await run_in_transaction(engine, method, *args, **kwargs)

    async def request(self, method, path, *args, **kwargs):
        """Make a request with the client."""
        headers = kwargs.setdefault('headers', {})
        headers['Content-Type'] = 'application/json;version=1.0'

        url = 'http://localhost:8080' + path
        method = getattr(self.client, method.lower())

        async with method(url, *args, **kwargs) as resp:
            await resp.text()
            return resp

    async def tearDown(self):
        self.client.close()
        super().tearDown()

    async def test_homepage(self):
        """The homepage shows a test message."""
        response = await self.request('GET', '/')
        self.assertEqual(200, response.status)
        self.assertEqual(
            'Basic authentication backend and API service.',
            await response.text())

    async def test_api_no_credentials(self):
        """Without credentials, access to API is denied."""
        response = await self.request('GET', '/api')
        self.assertEqual(401, response.status)
        self.assertEqual('401: Unauthorized', await response.text())

    async def test_api_wrong_credentials(self):
        """If unknown credentials are supplied, access to API is denied."""
        await self.call_model_method('add_credentials', 'foo', 'bar', 'baz')
        response = await self.request(
            'GET', '/api/credentials/foo',
            auth=aiohttp.BasicAuth('user', 'wrong'), json={})
        self.assertEqual(401, response.status)
        self.assertEqual('401: Unauthorized', await response.text())

    async def test_api_correct_credentials(self):
        """If correct credentials are supplied, access to API is allowed."""
        await self.call_model_method('add_credentials', 'foo', 'bar', 'baz')
        response = await self.request(
            'GET', '/api/credentials/foo',
            auth=aiohttp.BasicAuth('user', 'pass'), json={})
        self.assertEqual(200, response.status)
        self.assertEqual(
            {'user': 'foo', 'token': 'bar:baz'},
            await response.json())

    async def test_create_credentials(self):
        """It's possible to create credentials."""
        response = await self.request(
            'POST', '/api/credentials',
            auth=aiohttp.BasicAuth('user', 'pass'),
            json={'user': 'foo', 'token': 'bar:baz'})
        self.assertEqual(201, response.status)
        self.assertEqual(
            {'user': 'foo', 'token': 'bar:baz'},
            await response.json())
        creds = await self.call_model_method('get_credentials', 'foo')
        self.assertEqual('foo', creds.user)
        self.assertEqual('bar', creds.auth.username)
        self.assertEqual('baz', creds.auth.password)

    async def test_get_credentials(self):
        """It's possible to retrieve credentials."""
        await self.call_model_method('add_credentials', 'foo', 'bar', 'baz')
        response = await self.request(
            'GET', '/api/credentials/foo',
            auth=aiohttp.BasicAuth('user', 'pass'))
        self.assertEqual(200, response.status)
        self.assertEqual(
            {'user': 'foo', 'token': 'bar:baz'},
            await response.json())

    async def test_remove_credentials(self):
        """It's possible to remove credentials."""
        await self.call_model_method('add_credentials', 'foo', 'bar', 'baz')
        response = await self.request(
            'DELETE', '/api/credentials/foo',
            auth=aiohttp.BasicAuth('user', 'pass'))
        self.assertEqual(200, response.status)
        self.assertEqual({}, await response.json())
        self.assertIsNone(
            await self.call_model_method('get_credentials', 'foo'))

    async def test_update_credentials(self):
        """It's possible to update credentials."""
        await self.call_model_method('add_credentials', 'foo', 'bar', 'baz')
        response = await self.request(
            'PUT', '/api/credentials/foo',
            auth=aiohttp.BasicAuth('user', 'pass'),
            json={'token': 'new:token'})
        self.assertEqual(200, response.status)
        self.assertEqual(
            {'user': 'foo', 'token': 'new:token'},
            await response.json())
        creds = await self.call_model_method('get_credentials', 'foo')
        self.assertEqual('foo', creds.user)
        self.assertEqual('new', creds.auth.username)
        self.assertEqual('token', creds.auth.password)

    async def test_auth_check_no_auth(self):
        """The auth-check fails if no auth is provided."""
        response = await self.request('GET', '/auth-check')
        self.assertEqual(401, response.status)

    async def test_auth_check_invalid_auth(self):
        """The auth-check fails if invalid credentials are provided."""
        response = await self.request(
            'GET', '/auth-check', auth=aiohttp.BasicAuth('wrong', 'creds'))
        self.assertEqual(401, response.status)

    async def test_auth_check_valid_auth(self):
        """The auth check passes if valid credentials are provided."""
        await self.call_model_method('add_credentials', 'foo', 'bar', 'baz')
        response = await self.request(
            'GET', '/auth-check', auth=aiohttp.BasicAuth('bar', 'baz'))
        self.assertEqual(200, response.status)


def load_tests(loader, standard_tests, pattern):
    # top level directory cached on loader instance
    suite = testresources.OptimisingTestSuite()
    tests = loader.loadTestsFromTestCase(SystemTests)
    suite.addTests(tests)
    return suite
