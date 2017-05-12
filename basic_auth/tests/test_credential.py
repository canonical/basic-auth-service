from unittest import TestCase

from ..credential import BasicAuthCredentials


class BasicAuthCredentialsTest(TestCase):

    def test_generate(self):
        """It's possible to generate random BasicAuthCredentials."""
        creds = BasicAuthCredentials.generate()
        self.assertIsNotNone(creds.user)
        self.assertIsNotNone(creds.password)

    def test_random(self):
        """Generated credentials are random."""
        self.assertNotEqual(
            BasicAuthCredentials.generate(), BasicAuthCredentials.generate())

    def test_str(self):
        """BasicAuthCredentials can be printed as a token string."""
        creds = BasicAuthCredentials('foo', 'bar')
        self.assertEqual('foo:bar', str(creds))
