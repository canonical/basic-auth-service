import unittest
from contextlib import closing

import fixtures

import asynctest

import yaml

from ..server import (
    parse_args,
    load_config,
    create_app,
    main,
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


class CreateAppTest(unittest.TestCase):

    def test_create_app_set_config(self):
        """The configuration is set in the application."""
        config = {'sample': 'config'}
        app = create_app(config)
        self.assertIs(config, app['conf'])


class MainTest(asynctest.TestCase, fixtures.TestWithFixtures):

    def setUp(self):
        super().setUp()
        tmpdir = self.useFixture(fixtures.TempDir())
        self.config_path = tmpdir.join('config.yaml')
        with open(self.config_path, "w") as config_file:
            yaml.dump({}, config_file)

    @asynctest.fail_on(unused_loop=False)
    @asynctest.mock.patch("aiohttp.web.run_app")
    @asynctest.mock.patch("sys.stderr")
    def test_main_config_file_required(self, mock_stderr, mock_run_app):
        self.assertRaises(SystemExit, main, raw_args=[])

    @asynctest.fail_on(unused_loop=False)
    @asynctest.mock.patch("aiohttp.web.run_app")
    def test_main_calls_web_run_app(self, run_app):
        main(raw_args=[self.config_path])
        self.assertTrue(run_app.called)
