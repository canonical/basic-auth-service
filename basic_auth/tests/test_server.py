from contextlib import closing

import fixtures

import asynctest

import yaml

from ..testing import create_test_config
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
        create_test_config(filename=file_path)
        args = parse_args(args=[file_path])
        with closing(args.config):
            config = yaml.load(args.config.read())
        self.assertEqual(
            {'db': {'dsn': 'postgresql:///basic-auth-test'}},
            config)


class LoadConfigTest(fixtures.TestWithFixtures):

    def test_load_config(self):
        """The config is loaded from the file specified by args."""
        tempdir = self.useFixture(fixtures.TempDir())
        file_path = tempdir.join('config.yaml')
        create_test_config(filename=file_path)
        args = parse_args(args=[file_path])
        self.assertEqual(
            {'db': {'dsn': 'postgresql:///basic-auth-test'}},
            load_config(args))


class CreateAppTest(asynctest.TestCase):

    async def test_create_app_set_config(self):
        """The configuration is set in the application."""
        config = create_test_config()
        app = await create_app(config)
        self.assertIsNotNone(app['db'])
        app['db'].close()
        await app['db'].wait_closed()


class MainTest(asynctest.TestCase, fixtures.TestWithFixtures):

    forbid_get_event_loop = True

    def setUp(self):
        super().setUp()
        tmpdir = self.useFixture(fixtures.TempDir())
        self.config_path = tmpdir.join('config.yaml')
        create_test_config(filename=self.config_path)

    async def _close_db(self, run_app):
        """Close the DB in the app that was passed to the run_app call."""
        [[app], _] = run_app.call_args
        app["db"].terminate()
        await app["db"].wait_closed()

    @asynctest.mock.patch("aiohttp.web.run_app")
    @asynctest.mock.patch("sys.stderr")
    async def test_main_config_file_required(self, mock_stderr, mock_run_app):
        self.assertRaises(SystemExit, main, loop=self.loop, raw_args=[])

    @asynctest.mock.patch("aiohttp.web.run_app")
    async def test_main_calls_web_run_app(self, mock_run_app):
        self.addCleanup(self._close_db, mock_run_app)
        main(raw_args=[self.config_path])
        self.assertTrue(mock_run_app.called)
