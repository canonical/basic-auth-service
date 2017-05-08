"""Server entry point."""

import argparse

from aiohttp import web
import uvloop

from . import (
    __doc__ as description,
    handlers
)
from .middleware import BasicAuthMiddlewareFactory


def parse_args(args):
    parser = argparse.ArgumentParser(description=description)
    return parser.parse_args(args)


async def create_app():
    app = web.Application(middlewares=[BasicAuthMiddlewareFactory()])
    app.router.add_get('/', handlers.root)
    app.router.add_get('/auth-check', handlers.auth_check)
    app.router.add_get('/api', handlers.api)
    return app


def main(loop=None, raw_args=None):

    if loop is None:
        loop = uvloop.new_event_loop()

    app = loop.run_until_complete(create_app())
    web.run_app(app)
