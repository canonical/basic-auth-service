"""Server entry point."""

import argparse
import logging

from aiohttp import web

from aiopg.sa import create_engine

import uvloop

from .. import (
    handler,
    __doc__ as description,
)
from ..logging import setup_logging
from ..config import load_config
from ..collection import (
    DataBaseCredentialsCollection,
    MemoryCredentialsCollection,
)
from ..application import (
    setup_api_application,
    setup_auth_check_application,
)


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--config', help='Service configuration file',
        type=argparse.FileType(), default='config.yaml')
    return parser.parse_args(args=args)


async def create_app(conf, loop=None):
    """Create the base application."""
    app = web.Application(middlewares=[web.normalize_path_middleware()])

    if conf.get(('app', 'no-db')):
        collection = MemoryCredentialsCollection()
    else:
        engine = await create_engine(dsn=conf['db', 'dsn'], loop=loop)
        collection = DataBaseCredentialsCollection(engine)
        app['db'] = engine
    logging.getLogger().info(
        'Using collections class: {}'.format(
            collection.__class__.__name__))

    app.router.add_get('/', handler.root)
    app['subapps'] = {
        'api': app.add_subapp('/api', setup_api_application(collection)),
        'auth-check': app.add_subapp(
            '/auth-check', setup_auth_check_application(collection))}
    return app


def main(loop=None, raw_args=None):
    """Server main."""
    args = parse_args(args=raw_args)
    conf = load_config(args)
    setup_logging()

    if loop is None:
        loop = uvloop.new_event_loop()
    app = loop.run_until_complete(create_app(conf, loop=loop))
    web.run_app(app, port=8080, loop=loop)
