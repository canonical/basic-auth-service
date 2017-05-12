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
from .application import (
    setup_api_application,
    setup_auth_check_application,
)


def parse_args(args):
    parser = argparse.ArgumentParser(description=description)
    return parser.parse_args(args)


async def create_app():
    """Create the base application."""
    collection = CredentialsCollection()
    app = web.Application(middlewares=[web.normalize_path_middleware()])
    app.router.add_get('/', handler.root)
    app.add_subapp('/api', setup_api_application(collection))
    app.add_subapp('/auth-check', setup_auth_check_application(collection))
    return app


def main(loop=None, raw_args=None):
    if loop is None:
        loop = uvloop.new_event_loop()

    setup_logging()
    app = loop.run_until_complete(create_app())
    web.run_app(app, port=8080)
