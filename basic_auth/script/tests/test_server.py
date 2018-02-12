from contextlib import closing
from unittest import mock

import fixtures

import asynctest

import yaml

from ..server import (
    parse_args,
    create_app,
    main,
)
from ...testing import create_test_config


class ParseArgsTest(fixtures.TestWithFixtures):

    def test_parse_args(self):
        """Command line arguments are parsed."""
        tempdir = self.useFixture(fixtures.TempDir())
        file_path = tempdir.join('config.yaml')
        create_test_config(filename=file_path)
        args = parse_args(args=['--config', file_path])
        with closing(args.config):
            config = yaml.load(args.config.read())
        self.assertEqual(
            {'db': {'dsn': 'postgresql:///basic-auth-test'},
             'app': {'port': 8080}},
            config)


class CreateAppTest(asynctest.TestCase, fixtures.TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.useFixture(fixtures.LoggerFixture())

    async def _close_db(self, app):
        """Close the DB in the app."""
        app['db'].terminate()
        await app['db'].wait_closed()

    async def test_create_app_set_config(self):
        """The configuration is set in the application."""
        config = create_test_config()
        app = await create_app(config)
        self.assertIsNotNone(app['db'])
        await self._close_db(app)

    @mock.patch('aiopg.sa.create_engine')
    async def test_create_app_no_db(self, mock_create_engine):
        """If the "no-db" config is specified, memory collection is used."""
        config = create_test_config(use_db=False)
        app = await create_app(config)
        self.assertIsNone(app.get('db'))
        self.assertFalse(mock_create_engine.called)


class MainTest(asynctest.TestCase, fixtures.TestWithFixtures):

    forbid_get_event_loop = True

    def setUp(self):
        super().setUp()
        self.useFixture(fixtures.LoggerFixture())
        tmpdir = self.useFixture(fixtures.TempDir())
        self.config_path = tmpdir.join('config.yaml')
        create_test_config(filename=self.config_path)

    async def _close_db(self, run_app):
        """Close the DB in the app that was passed to the run_app call."""
        [[app], _] = run_app.call_args
        app['db'].terminate()
        await app['db'].wait_closed()

    @asynctest.mock.patch('aiohttp.web.run_app')
    @asynctest.mock.patch('basic_auth.script.server.setup_logging')
    # TODO frankban: reenable.
    async def disable_test_main_calls_web_run_app(self, _, mock_run_app):
        """The script main runs the web application."""
        self.addCleanup(self._close_db, mock_run_app)
        main(raw_args=['--config', self.config_path])
        mock_run_app.assert_called_with(mock.ANY, loop=mock.ANY, port=8080)

    @asynctest.mock.patch('aiohttp.web.run_app')
    @asynctest.mock.patch('basic_auth.script.server.setup_logging')
    # TODO frankban: reenable.
    async def disable_test_main_server_port(self, _, mock_run_app):
        """A different application port can be specified in config file."""
        create_test_config(filename=self.config_path, port=9090)
        self.addCleanup(self._close_db, mock_run_app)
        main(raw_args=['--config', self.config_path])
        mock_run_app.assert_called_with(mock.ANY, loop=mock.ANY, port=9090)
