"""Server entry point."""

from contextlib import closing
import argparse

import yaml

from aiohttp import web

import uvloop

from . import (
    handler,
    __doc__ as description,
)
from .logging import setup_logging
from .collection import CredentialsCollection
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


def create_app(conf):
    """Create the base application."""
    collection = CredentialsCollection()
    app = web.Application(middlewares=[web.normalize_path_middleware()])
    app['conf'] = conf
    app.router.add_get('/', handler.root)
    app.add_subapp('/api', setup_api_application(collection))
    app.add_subapp('/auth-check', setup_auth_check_application(collection))
    return app


def main(loop=None, raw_args=None):
    """Server main."""
    args = parse_args(args=raw_args)
    setup_logging()
    conf = load_config(args)
    app = create_app(conf)
    if loop is None:
        loop = uvloop.new_event_loop()
    web.run_app(app, port=8080, loop=loop)
