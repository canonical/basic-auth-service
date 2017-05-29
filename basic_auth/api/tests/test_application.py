import json

from aiohttp import web
from aiohttp.test_utils import unittest_run_loop

from ..testing import (
    APITestCase,
    APIApplicationTestCase,
)
from ..sample import (
    SampleCreateSchema,
    SampleUpdateSchema,
    SampleResourceCollection,
)
from ..application import (
    ResourceEndpoint,
    APIApplication,
)
from ..resource import APIResource


class SampleResourceEndpoint(ResourceEndpoint):

    collection_methods = frozenset(['POST'])
    instance_methods = frozenset(['GET'])


class ResourceEndpointTest(APITestCase):

    def setUp(self):
        self.collection = SampleResourceCollection()
        self.resource = APIResource(
            self.collection, SampleCreateSchema, SampleUpdateSchema)
        self.endpoint = SampleResourceEndpoint('sample', self.resource)
        super().setUp()

    def create_app(self):
        app = APIApplication()
        app.register_endpoint(self.endpoint)
        return app

    async def test_handle_collection_create(self):
        """The create method returns a Created response with details."""
        content = {'id': 'foo', 'value': 'bar'}
        request = self.get_request(method='POST', content=content)
        response = await self.endpoint.handle_collection(request)
        self.assertEqual(201, response.status)
        self.assertEqual(content, json.loads(response.text))

    async def test_handle_collection_other(self):
        """Non-create methods return Ok if the operation has success."""
        content = {'id': 'foo', 'value': 'bar'}
        await self.collection.create(content)

        # Add a non-create method on the resource
        self.endpoint.collection_methods = frozenset(['GET'])
        self.endpoint._collection_methods_map = {'GET': 'get_collection'}

        async def get_collection(request):
            return [content]

        self.resource.get_collection = get_collection
        request = self.get_request(method='GET', content=content)
        response = await self.endpoint.handle_collection(request)
        self.assertEqual(200, response.status)
        self.assertEqual([content], json.loads(response.text))

    async def test_handle_collection_method_not_allowed(self):
        """handle_collection return an error for not allowed methods."""
        request = self.get_request(method='PUT')
        with self.assertRaises(web.HTTPMethodNotAllowed) as cm:
            await self.endpoint.handle_collection(request)
        response = cm.exception
        self.assertEqual(405, response.status_code)
        self.assertEqual(
            {'code': 'Method Not Allowed',
             'message': 'Only POST requests are allowed'},
            json.loads(response.text))

    async def test_handle_collection_only_implemented_method(self):
        """Only implemented methods are accepted in collection_methods."""
        # PATCH is not implemented
        self.endpoint.instance_methods = frozenset(['POST', 'PATCH'])

        request = self.get_request(method='PATCH')
        with self.assertRaises(web.HTTPMethodNotAllowed) as cm:
            await self.endpoint.handle_collection(request)
        response = cm.exception
        self.assertEqual(405, response.status_code)
        self.assertEqual(
            {'code': 'Method Not Allowed',
             'message': 'Only POST requests are allowed'},
            json.loads(response.text))

    async def test_handle_instance(self):
        """Allowed methods can be called on handle_instance."""
        content = {'id': 'foo', 'value': 'bar'}
        await self.collection.create(content)
        request = self.get_request()
        response = await self.endpoint.handle_instance(request, 'foo')
        self.assertEqual(200, response.status)

    async def test_handle_instance_not_found(self):
        """Resource errors are converted to corresponding HTTP errors."""
        request = self.get_request()
        response = await self.endpoint.handle_instance(request, 'foo')
        self.assertEqual(404, response.status)
        self.assertEqual(
            {'code': 'Not Found',
             'message': 'Resource with ID "foo" not found'},
            json.loads(response.text))

    async def test_handle_instance_method_not_allowed(self):
        """handle_collection return an error for not allowed methods."""
        request = self.get_request(method='POST')
        with self.assertRaises(web.HTTPMethodNotAllowed) as cm:
            await self.endpoint.handle_instance(request, 'foo')
        response = cm.exception
        self.assertEqual(405, response.status_code)
        self.assertEqual(
            {'code': 'Method Not Allowed',
             'message': 'Only GET requests are allowed'},
            json.loads(response.text))

    async def test_handle_instance_only_implemented_methods(self):
        """Only implemented methods are accepted in instance_methods."""
        # PATCH is not implemented
        self.endpoint.instance_methods = frozenset(['GET', 'PATCH'])

        request = self.get_request(method='PATCH')
        with self.assertRaises(web.HTTPMethodNotAllowed) as cm:
            await self.endpoint.handle_instance(request, 'foo')
        response = cm.exception
        self.assertEqual(405, response.status_code)
        self.assertEqual(
            {'code': 'Method Not Allowed',
             'message': 'Only GET requests are allowed'},
            json.loads(response.text))

    async def test_request_invalid_payload(self):
        """An invalid JSON payload returns a Bad Request error."""
        request = self.get_request(
            method='POST', content=b'garbage', json_encode=False)
        with self.assertRaises(web.HTTPBadRequest) as cm:
            await self.endpoint.handle_collection(request)
        response = cm.exception
        self.assertEqual(400, response.status)
        self.assertEqual(
            'Invalid JSON payload', json.loads(response.text)['message'])


class APIApplicationTest(APIApplicationTestCase):

    def setUp(self):
        self.collection = SampleResourceCollection()
        self.resource = APIResource(
            self.collection, SampleCreateSchema, SampleUpdateSchema)
        self.endpoint = SampleResourceEndpoint('sample', self.resource)
        super().setUp()

    async def get_application(self):
        app = APIApplication()
        app.register_endpoint(self.endpoint)
        return app

    @unittest_run_loop
    async def test_request_collection(self):
        """A request to the collection URL calls the appropriate handler."""
        content = {'id': 'foo', 'value': 'bar'}
        response = await self.client_request(
            method='POST', path='/sample', json=content)
        self.assertEqual(201, response.status)
        self.assertEqual(content, await response.json())
        self.assertEqual('/sample/foo', response.headers['Location'])

    @unittest_run_loop
    async def test_request_instance(self):
        """A request to the instance URL calls the appropriate handler."""
        content = {'id': 'foo', 'value': 'bar'}
        await self.collection.create(content)
        await self.client_request(
            method='POST', path='/sample', json=content)
        response = await self.client_request(path='/sample/foo')
        self.assertEqual(200, response.status)
        self.assertEqual(content, await response.json())

    @unittest_run_loop
    async def test_request_missing_version_mime_type(self):
        """If API version is not provided an error is returned."""
        self.app.version = '1.0'
        content = {'id': 'foo', 'value': 'bar'}
        response = await self.client_request(
            method='POST', path='/sample', json=content)
        self.assertEqual(400, response.status)
        self.assertEqual(
            {'code': 'Bad Request',
             'message': 'Invalid request MIME type'},
            await response.json())

    @unittest_run_loop
    async def test_request_missing_profile_mime_type(self):
        """If API profile is not provided an error is returned."""
        self.app.profile = 'myapp'
        content = {'id': 'foo', 'value': 'bar'}
        response = await self.client_request(
            method='POST', path='/sample', json=content)
        self.assertEqual(400, response.status)
        self.assertEqual(
            {'code': 'Bad Request',
             'message': 'Invalid request MIME type'},
            await response.json())

    @unittest_run_loop
    async def test_request_profile_and_version(self):
        """IF API profile and version are specified, no error is raised."""
        self.app.profile = 'myapp'
        self.app.version = '1.0'
        content = {'id': 'foo', 'value': 'bar'}
        response = await self.client_request(
            method='POST', path='/sample',
            content_type='application/json; profile=myapp; version=1.0',
            json=content)
        self.assertEqual(201, response.status)
