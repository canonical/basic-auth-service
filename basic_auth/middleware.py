"""AioHTTP middlewares."""

from aiohttp import (
    web,
    BasicAuth,
)


class BaseBasicAuthMiddlewareFactory:
    """A middleware for handling Basic Authorization."""

    def __init__(self, realm):
        self.realm = realm

    async def is_valid_auth(self, user, password):
        """Return whether the basic-authorization si valid.

        It should be overridden by subclasses.
        """
        return False

    async def __call__(self, app, handler):
        """Return the middleware handler."""

        async def middleware_handler(request):
            if not await self._validate_auth(request):
                headers = {
                    'WWW-Authenticate': 'Basic realm="{}"'.format(self.realm)}
                return web.HTTPUnauthorized(headers=headers)

            return await handler(request)

        return middleware_handler

    async def _validate_auth(self, request):
        """Validate Basic-Auth in a request."""
        basic_auth = request.headers.get('Authorization')
        if not basic_auth:
            return False

        auth = BasicAuth.decode(basic_auth)
        return await self.is_valid_auth(auth.login, auth.password)


class BasicAuthMiddlewareFactory(BaseBasicAuthMiddlewareFactory):
    """Basic-Auth middleware using a checker method to verify credentials

    The checker function signature is as follows:

      async def checker(user, password) -> bool

    """

    def __init__(self, realm, checker):
        super().__init__(realm)
        self.checker = checker

    async def is_valid_auth(self, user, password):
        return await self.checker(user, password)
