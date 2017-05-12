"""Logging helpers."""

import sys
import logging


def setup_logging(log_stream=sys.stdout):
    """Set up the logging loggers and handlers.

    Two loggers are set up.
        - The root logger which catches all log messages, except for the
          access log
        - The access logger, which logs everything from aiohttp.access,
          which is logged with information about each request.

    The handlers for these two loggers both log to the same log stream,
    but the format is different, since the access logger already has all
    the information in the message itself.

    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    root_handler = logging.StreamHandler(log_stream)
    root_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    root_handler.setFormatter(formatter)
    root.addHandler(root_handler)

    access = logging.getLogger('aiohttp.access')
    access.setLevel(logging.INFO)
    access_handler = logging.StreamHandler(log_stream)
    access_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    access_handler.setFormatter(formatter)
    access.addHandler(access_handler)
    access.propagate = False
