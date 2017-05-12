from contextlib import closing

import yaml

import fixtures

from ..config import (
    parse_args,
    load_config,
)


class ParseArgsTest(fixtures.TestWithFixtures):

    def test_parse_args(self):
        """Command line arguments are parsed."""
        tempdir = self.useFixture(fixtures.TempDir())
        file_path = tempdir.join('config.yaml')
        with open(file_path, 'w') as fd:
            yaml.dump({'some': 'config'}, stream=fd)

        args = parse_args(args=[file_path])
        with closing(args.config):
            config = yaml.load(args.config.read())
        self.assertEqual({'some': 'config'}, config)


class LoadConfigTest(fixtures.TestWithFixtures):

    def test_load_config(self):
        """The config is loaded from the file specified by args."""
        tempdir = self.useFixture(fixtures.TempDir())
        file_path = tempdir.join('config.yaml')
        with open(file_path, 'w') as fd:
            yaml.dump({'some': 'config'}, stream=fd)

        args = parse_args(args=[file_path])
        self.assertEqual({'some': 'config'}, load_config(args))
