"""Server entry point."""

import argparse

from aiohttp import web
import uvloop

from . import (
    __doc__ as description,
    handler,
)
from .logging import setup_logging
from .collection import CredentialsCollection
from .middleware import BasicAuthMiddlewareFactory
from .application import (
    BasicAuthCheckApplication,
    setup_api_application,
)


def parse_args(args):
    parser = argparse.ArgumentParser(description=description)
    return parser.parse_args(args)


async def create_app():
    """Create the base application."""
    collection = CredentialsCollection()
    auth_middleware_factory = BasicAuthMiddlewareFactory(
        'auth-check', collection)
    app = web.Application(middlewares=[web.normalize_path_middleware()])
    app.router.add_get('/', handler.root)
    app.add_subapp(
        '/auth-check', BasicAuthCheckApplication(auth_middleware_factory))
    app.add_subapp('/api', setup_api_application(collection))
    return app


def main(loop=None, raw_args=None):
    if loop is None:
        loop = uvloop.new_event_loop()

    setup_logging()
    app = loop.run_until_complete(create_app())
    web.run_app(app, port=8080)
