"""AioHTTP applications."""

from aiohttp import web

from .middleware import BaseBasicAuthMiddlewareFactory


class BasicAuthCheckApplication(web.Application):

    def __init__(self, realm, auth_middleware=BaseBasicAuthMiddlewareFactory,
                 *args, **kwargs):
        # Add the authentication middleware
        kwargs.setdefault('middlewares', []).append(auth_middleware(realm))

        super().__init__(*args, **kwargs)
        self.router.add_get('/', self.check)

    async def check(self, request):
        """Handler for validating basic-auth."""
        # This can just return OK, since if the method is called credentials
        # are valid.
        return web.HTTPOk()
