"""AioHTTP middlewares."""

from aiohttp import (
    web,
    BasicAuth,
)


class BaseBasicAuthMiddlewareFactory:
    """A middleware for handling Basic Authentication."""

    def is_valid_auth(self, realm, user, password):
        """Return whether the basic authentication si valid.

        It should be overridden by subclasses.
        """
        return False

    async def __call__(self, app, handler):
        """Return the middleware handler."""

        async def middleware_handler(request):
            auth_realm = getattr(handler, '_basic_auth_realm', None)
            if auth_realm and not self._validate_auth(request, auth_realm):
                headers = {
                    'WWW-Authenticate': 'Basic realm="{}"'.format(auth_realm)}
                return web.HTTPUnauthorized(headers=headers)

            return await handler(request)

        return middleware_handler

    def _validate_auth(self, request, auth_realm):
        """Validate Basic-Auth in a request."""
        basic_auth = request.headers.get('Authorization')
        if not basic_auth:
            return False

        auth = BasicAuth.decode(basic_auth)
        return self.is_valid_auth(auth_realm, auth.login, auth.password)


class BasicAuthMiddlewareFactory(BaseBasicAuthMiddlewareFactory):

    pass


def basic_auth_realm(realm):
    """Decorator to set the basic-auth realm for a handler."""

    def deco(handler):
        handler._basic_auth_realm = realm
        return handler

    return deco
