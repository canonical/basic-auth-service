"""Server entry point."""

from contextlib import closing
import argparse

import yaml

from aiohttp import web

from aiopg.sa import create_engine

import uvloop

from . import (
    handler,
    __doc__ as description,
)
from .logging import setup_logging
from .collection import DataBaseCredentialsCollection
from .application import (
    setup_api_application,
    setup_auth_check_application,
)


def parse_args(args=None):
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', type=argparse.FileType())
    return parser.parse_args(args=args)


def load_config(args):
    """Return a dict with configuration from the config file.

    The args argument must be an argparse.Namespace instance.

    """
    with closing(args.config):
        return yaml.load(args.config)


async def create_app(conf, loop=None):
    """Create the base application."""
    engine = await create_engine(dsn=conf['db']['dsn'], loop=loop)
    collection = DataBaseCredentialsCollection(engine)
    app = web.Application(middlewares=[web.normalize_path_middleware()])
    app['db'] = engine
    app.router.add_get('/', handler.root)
    app.add_subapp('/api', setup_api_application(collection))
    app.add_subapp('/auth-check', setup_auth_check_application(collection))
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
