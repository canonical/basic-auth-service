import io
import logging

import fixtures

from ..logging import setup_logging


class SetupLoggingTest(fixtures.TestWithFixtures):

    def setUp(self):
        super().setUp()
        self.useFixture(fixtures.FakeLogger())

    def test_set_up_logging_root(self):
        """setup_loggingsets up a log handler for the given IO stream."""
        log_stream = io.StringIO()
        setup_logging(log_stream)
        logging.info('Some info')
        logged_content = log_stream.getvalue()
        self.assertIn('root - INFO - Some info', logged_content)
