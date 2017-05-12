"""Server entry point."""

import argparse

from aiohttp import web
import uvloop

from . import (
    __doc__ as description,
    handler,
    api,
)
from .api.sample import (
    SampleCreateSchema,
    SampleUpdateSchema,
    SampleResourceCollection,
)
from .application import BasicAuthCheckApplication


def parse_args(args):
    parser = argparse.ArgumentParser(description=description)
    return parser.parse_args(args)


async def create_app():
    """Create the base application."""
    app = web.Application()
    app.router.add_get('/', handler.root)
    app.add_subapp('/auth-check', BasicAuthCheckApplication('auth-check'))
    # setup API application
    api_app = api.APIApplication()
    # XXX temporary sample setup
    resource = api.APIResource(
        SampleResourceCollection(), SampleCreateSchema, SampleUpdateSchema)
    endpoint = api.ResourceEndpoint('credentials', resource, '1.0')
    endpoint.collection_methods = frozenset(['POST'])
    endpoint.instance_methods = frozenset(['GET', 'PUT', 'DELETE'])
    api_app.register_endpoint(endpoint)
    app.add_subapp('/api', api_app)
    return app


def main(loop=None, raw_args=None):
    if loop is None:
        loop = uvloop.new_event_loop()

    app = loop.run_until_complete(create_app())
    web.run_app(app)
