import argparse
import unittest

import fixtures

from ..config import (
    Config,
    load_config,
)
from ..testing import create_test_config


class ConfigTest(unittest.TestCase):

    def test_config_from_dict(self):
        """A Config can be created from a dict."""
        config = Config({'foo': 'bar', 'baz': 33})
        self.assertEqual('bar', config['foo'])
        self.assertEqual(33, config['baz'])

    def test_asdict(self):
        """Config.asdict returns a dict with the config."""
        source = {'foo': 'bar', 'baz': 33}
        config = Config(source)
        self.assertEqual(source, config.asdict())

    def test_asdict_copy(self):
        """Config.asdict returns a copy of the original dict."""
        source = {'foo': 'bar', 'baz': 33}
        config = Config(source)
        source['foo'] = 'changed'
        self.assertEqual('bar', config.asdict()['foo'])

    def test_getitem(self):
        """Items can be accessed from the Config."""
        config = Config({'foo': 'bar'})
        self.assertEqual('bar', config['foo'])

    def test_getitem_nested(self):
        """Passing a tuple to getitems traveses the config."""
        config = Config({'foo': {'bar': 'baz'}})
        self.assertEqual('baz', config['foo', 'bar'])

    def test_getitem_nested_no_nested_dict(self):
        """KeyError is raised if a subelement is not a dict."""
        config = Config({'foo': 'bar'})
        with self.assertRaises(KeyError):
            config['foo', 'bar']

    def test_get(self):
        """Config.get returns the config item."""
        config = Config({'foo': {'bar': 'baz'}})
        self.assertEqual('baz', config.get(('foo', 'bar')))

    def test_get_not_found(self):
        """Config.get returns None if the element is not found."""
        config = Config({'foo': {'bar': 'baz'}})
        self.assertIsNone(config.get(('foo', 'not-here')))

    def test_get_not_found_default(self):
        """Config.get returns the default if the element is not found."""
        config = Config({'foo': {'bar': 'baz'}})
        self.assertEqual('asdf', config.get(('foo', 'not-here'), 'asdf'))

    def test_equal_true(self):
        """Two Configs with the same details are equal."""
        config1 = Config({'foo': {'bar': 'baz'}})
        config2 = Config({'foo': {'bar': 'baz'}})
        self.assertTrue(config1 == config2)

    def test_equal_false(self):
        """Two Configs with different details are not equal."""
        config1 = Config({'foo': {'bar': 'baz'}})
        config2 = Config({'foo': {'bar': 'bza'}})
        self.assertFalse(config1 == config2)


class LoadConfigTest(fixtures.TestWithFixtures):

    def test_load_config(self):
        """The config is loaded from the file specified by args."""
        tempdir = self.useFixture(fixtures.TempDir())
        file_path = tempdir.join('config.yaml')
        create_test_config(filename=file_path)
        # simulate parsing commandline
        args = argparse.Namespace(config=open(file_path))
        self.assertEqual(
            {'db': {'dsn': 'postgresql:///basic-auth-test'}},
            load_config(args).asdict())
