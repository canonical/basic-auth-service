"""HTTP handlers."""

from aiohttp import web

from . import __doc__ as description


async def root(request):
    """Base resource."""
    return web.Response(text=description)
