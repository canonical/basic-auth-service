"""Testing helper for database setup."""

import os
import io
import logging

import asynctest

from aiopg.sa import create_engine

import sqlalchemy

from alembic.config import Config
from alembic import command

from ..testing import TEST_DB_DSN
from .schema import METADATA


class DataBaseTest(asynctest.TestCase):

    forbid_get_event_loop = True

    async def setUp(self):
        super().setUp()
        ensure_database()
        self.engine = await create_engine(dsn=TEST_DB_DSN, loop=self.loop)
        self.conn = await self.engine.acquire()
        self.txn = await self.conn.begin()

    async def tearDown(self):
        self.engine.terminate()
        await self.engine.wait_closed()
        super().tearDown()


def ensure_database(dsn=TEST_DB_DSN):
    """Ensure that a clean database is available for tests."""
    engine = sqlalchemy.create_engine(dsn)
    path_to_alembic = os.path.abspath(
        os.path.join(os.getcwd(), 'templates/alembic.ini'))
    output_buffer = io.BytesIO()
    alembic_cfg = Config(path_to_alembic, output_buffer=output_buffer)
    alembic_cfg.set_section_option('alembic', 'sqlalchemy.url', dsn)
    alembic_cfg.set_section_option('loggers', 'keys', '')
    with engine.begin() as connection:
        alembic_cfg.attributes['connection'] = connection
        logging.disable(logging.ERROR)
        command.upgrade(alembic_cfg, 'head')
        logging.disable(logging.NOTSET)
        for table in reversed(METADATA.sorted_tables):
            connection.execute(table.delete())
    engine.dispose()
