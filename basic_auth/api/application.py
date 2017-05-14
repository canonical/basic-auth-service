"""REST API application."""

from functools import wraps
import json

from aiohttp import web
from aiohttp.helpers import parse_mimetype

from .response import (
    APIResponse,
    APIError,
)
from .error import to_api_error


class ResourceEndpoint:
    """API endpoint for a resource type."""

    # Allowed HTTP methods for collection and instances requests.  Subclasses
    # can change these.
    collection_methods = frozenset(['POST'])
    instance_methods = frozenset(['GET', 'PUT', 'DELETE'])

    _collection_methods_map = {
        'POST': 'create',
    }
    _instance_methods_map = {
        'GET': 'get',
        'DELETE': 'delete',
        'PUT': 'update',
    }

    def __init__(self, name, resource, version='1.0'):
        self.name = name
        self.resource = resource
        self.version = version

    async def handle_collection(self, request):
        """Handle a request for a collection."""
        allowed_methods = self.collection_methods.intersection(
            self._collection_methods_map)
        payload = await self._validate_request(request, allowed_methods)

        func = getattr(
            self.resource, self._collection_methods_map[request.method])
        try:
            result = await func(payload)
        except Exception as error:
            return to_api_error(error)

        if request.method == 'POST':
            # The create method returns the resource ID too.
            res_id, content = result
            url = request.app.router['instance'].url_for(instance_id=res_id)
            headers = {'Location': str(url)}
            return APIResponse(
                content=content, response='Created', headers=headers)
        else:
            return APIResponse(content=result)

    async def handle_instance(self, request, instance_id):
        """Handle a request for an instance."""
        allowed_methods = self.instance_methods.intersection(
            self._instance_methods_map)
        payload = await self._validate_request(request, allowed_methods)

        func = getattr(
            self.resource, self._instance_methods_map[request.method])
        try:
            content = await func(instance_id, payload)
        except Exception as error:
            return to_api_error(error)

        return APIResponse(content=content)

    async def _validate_request(self, request, allowed_methods):
        """Check that the request is valid and return the decoded payload."""
        self._check_method_allowed(request, allowed_methods)
        self._check_valid_mimetype(request)
        if not request.content_length:
            return
        try:
            return await request.json()
        except json.JSONDecodeError:
            raise APIError('BadRequest', message='Invalid JSON payload')

    def _check_method_allowed(self, request, allowed_methods):
        if request.method not in allowed_methods:
            message = 'Only {} requests are allowed'.format(
                ','.join(sorted(allowed_methods)))
            raise APIError(
                'MethodNotAllowed', request.method, allowed_methods,
                message=message)

    def _check_valid_mimetype(self, request):
        typ, subtype, suffix, params = parse_mimetype(
            request.headers.get('Content-Type'))
        valid_type = (typ, subtype, suffix) == ('application', 'json', '')
        valid_version = params.get('version') == self.version
        if not valid_type or not valid_version:
            raise APIError('BadRequest', message='Invalid request MIME type')


class APIApplication(web.Application):
    """The REST API application."""

    def register_endpoint(self, endpoint):
        self.router.add_route(
            '*', '/{name}'.format(name=endpoint.name),
            endpoint.handle_collection, name='collection')
        self.router.add_route(
            '*', '/{name}/{{instance_id}}'.format(name=endpoint.name),
            self._wrap_handle_instance(endpoint.handle_instance),
            name='instance')

    def _wrap_handle_instance(self, handle_instance):
        """Wrap handle_instance handler to pass the ID as parameter."""

        @wraps(handle_instance)
        async def wrapper(request):
            instance_id = request.match_info['instance_id']
            return await handle_instance(request, instance_id)

        return wrapper
