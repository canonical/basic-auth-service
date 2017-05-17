from contextlib import closing

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
            {'db': {'dsn': 'postgresql:///basic-auth-test'}},
            config)


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
    async def test_main_calls_web_run_app(self, mock_run_app):
        """The script main runs the web application."""
        self.addCleanup(self._close_db, mock_run_app)
        main(raw_args=['--config', self.config_path])
        self.assertTrue(mock_run_app.called)
