"""Configuration handling functions."""

from contextlib import closing
import copy

import yaml


class Config:
    """Application configuration."""

    def __init__(self, config_dict):
        self._conf = copy.deepcopy(config_dict)

    def __getitem__(self, key):
        if not isinstance(key, (tuple, list)):
            return self._conf[key]

        conf = self._conf
        for token in key:
            if not isinstance(conf, dict):
                raise KeyError(token)
            conf = conf[token]
        return conf

    def __eq__(self, other):
        return self.asdict() == other.asdict()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def asdict(self):
        """Return a dict with the config."""
        return copy.deepcopy(self._conf)


def load_config(args):
    """Return a dict with configuration from the config file.

    The args argument must be an argparse.Namespace instance.

    """
    with closing(args.config):
        return Config(yaml.load(args.config))
