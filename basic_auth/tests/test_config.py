import argparse

import fixtures

from ..config import load_config
from ..testing import create_test_config


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
            load_config(args))
