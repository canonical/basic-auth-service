"""Configuration handling functions."""

from contextlib import closing

import yaml


def load_config(args):
    """Return a dict with configuration from the config file.

    The args argument must be an argparse.Namespace instance.

    """
    with closing(args.config):
        return yaml.load(args.config)
