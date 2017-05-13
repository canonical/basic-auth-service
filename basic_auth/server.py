"""Server entry point."""

from aiohttp import web
import uvloop

from . import handler
from .logging import setup_logging
from .config import (
    parse_args,
    load_config,
)
from .collection import CredentialsCollection
from .application import (
    setup_api_application,
    setup_auth_check_application,
)


def create_app():
    """Create the base application."""
    collection = CredentialsCollection()
    app = web.Application(middlewares=[web.normalize_path_middleware()])
    app.router.add_get('/', handler.root)
    app.add_subapp('/api', setup_api_application(collection))
    app.add_subapp('/auth-check', setup_auth_check_application(collection))
    return app


def main():
    """Server main."""
    args = parse_args()
    setup_logging()
    conf = load_config(args)
    app = create_app(conf)
    loop = uvloop.new_event_loop()
    web.run_app(app, port=8080, loop=loop)
