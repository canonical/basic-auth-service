"""AioHTTP applications."""

from aiohttp import web

from .schema import (
    CredentialsCreateSchema,
    CredentialsUpdateSchema,
)
from .api import (
    APIApplication,
    ResourceEndpoint,
    APIResource,
)
from .middleware import BasicAuthMiddlewareFactory


class BasicAuthCheckApplication(web.Application):
    """Application for checking Basic-Auth credentials.

    It provides a root resource which returns a 200 status if credentials are
    valid, 401 otherwise.

    """

    def __init__(self, auth_middleware_factory, *args, **kwargs):
        # Add the authentication middleware
        kwargs.setdefault('middlewares', []).append(auth_middleware_factory)

        super().__init__(*args, **kwargs)
        self.router.add_get('/', self.check)

    async def check(self, request):
        """Handler for validating basic-auth."""
        # This can just return OK, since if the method is called credentials
        # are valid.
        return web.HTTPOk()


def setup_api_application(collection):
    """Setup an APIApplication."""
    auth_middleware_factory = BasicAuthMiddlewareFactory(
        'api', collection.api_credentials_match)
    app = APIApplication(
        profile='basic-auth.api', version='1.0',
        middlewares=[auth_middleware_factory])
    resource = APIResource(
        collection, CredentialsCreateSchema, CredentialsUpdateSchema)
    endpoint = ResourceEndpoint('credentials', resource)
    app.register_endpoint(endpoint)
    return app


def setup_auth_check_application(collection):
    """Setup a BasicAuthCheckApplication."""
    auth_middleware_factory = BasicAuthMiddlewareFactory(
        'auth-check', collection.credentials_match)
    return BasicAuthCheckApplication(auth_middleware_factory)
