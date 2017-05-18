from unittest import TestCase

from ..credential import (
    BasicAuthCredentials,
    generate_random_token,
)


class BasicAuthCredentialsTest(TestCase):

    def test_generate(self):
        """It's possible to generate random BasicAuthCredentials."""
        creds = BasicAuthCredentials.generate()
        self.assertIsNotNone(creds.username)
        self.assertIsNotNone(creds.password)

    def test_from_token(self):
        """BasicAuthCredentials can be created from a "user:password" token."""
        creds = BasicAuthCredentials.from_token('foo:bar')
        self.assertEqual('foo', creds.username)
        self.assertEqual('bar', creds.password)

    def test_random(self):
        """Generated credentials are random."""
        self.assertNotEqual(
            BasicAuthCredentials.generate(), BasicAuthCredentials.generate())

    def test_str(self):
        """BasicAuthCredentials can be printed as a token string."""
        creds = BasicAuthCredentials('foo', 'bar')
        self.assertEqual('foo:bar', str(creds))


class GenerateRandomTokenTest(TestCase):

    def test_generate(self):
        """It's possible to generate a random token."""
        token = generate_random_token()
        self.assertIsInstance(token, str)

    def test_random(self):
        """Random tokens are generated."""
        self.assertNotEqual(generate_random_token(), generate_random_token())

    def test_length(self):
        """Tokens are generated with the specified length."""
        self.assertEqual(20, len(generate_random_token()))
        self.assertEqual(10, len(generate_random_token(length=10)))
        self.assertEqual(30, len(generate_random_token(length=30)))
