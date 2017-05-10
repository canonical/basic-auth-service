import json

from aiohttp import web
from aiohttp.test_utils import (
    unittest_run_loop,
)

from ..testing import (
    APITestCase,
    APIApplicationTestCase,
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
        super().setUp()
        self.resource = APIResource(None, None)
        self.endpoint = SampleResourceEndpoint('sample', self.resource, '1.0')

    async def test_handle_collection(self):
        """Allowed methods can be called on handle_collection."""
        request = self.get_request(method='POST')
        response = await self.endpoint.handle_collection(request)
        self.assertEqual(200, response.status)

    async def test_handle_collection_method_not_allowed(self):
        """handle_collection return an error for not allowed methods."""
        request = self.get_request(method='PUT')
        with self.assertRaises(web.HTTPMethodNotAllowed) as cm:
            await self.endpoint.handle_collection(request)
        response = cm.exception
        self.assertEqual(405, response.status_code)

    async def test_handle_collectione_only_implemented_method(self):
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
        request = self.get_request()
        response = await self.endpoint.handle_instance(request, 'foo')
        self.assertEqual(200, response.status)

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

    async def test_request_invalid_mime_type(self):
        """An invalid MIME type returns a Bad Request error."""
        # no version info in the Content-Type
        request = self.get_request(
            method='POST', content_type='application/json')
        with self.assertRaises(web.HTTPBadRequest) as cm:
            await self.endpoint.handle_collection(request)
        response = cm.exception
        self.assertEqual(400, response.status)
        self.assertEqual(
            'Invalid request MIME type', json.loads(response.text)['message'])

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
        self.resource = APIResource(None, None)
        self.endpoint = SampleResourceEndpoint('sample', self.resource, '1.0')
        super().setUp()

    async def get_application(self):
        app = APIApplication()
        app.register_endpoint(self.endpoint)
        return app

    @unittest_run_loop
    async def test_request_collection(self):
        """A request to the collection URL calls the appropriate handler."""
        response = await self.client_request(method='POST', path='/sample')
        self.assertEqual('{}', await response.text())

    @unittest_run_loop
    async def test_request_instance(self):
        """A request to the instance URL calls the appropriate handler."""
        response = await self.client_request(path='/sample/foo')
        self.assertEqual({'id': 'foo'}, await response.json())
