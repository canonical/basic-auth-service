"""Server HTTP handlers."""

from aiohttp import web

from . import __doc__ as description
from .middleware import basic_auth_realm


async def root(request):
    """Base resource."""
    return web.Response(text=description)


@basic_auth_realm('auth-check')
async def auth_check(request):
    """Handler for validating basic-auth."""
    return web.HTTPOk()


# XXX this should be behind auth
async def api(request):
    """Handler for validating basic-auth."""
    return web.HTTPOk()  # XXX
