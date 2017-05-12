"""Configuration functions."""

import argparse
from contextlib import closing

import yaml

from . import __doc__ as description


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
