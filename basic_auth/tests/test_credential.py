from unittest import TestCase

from ..credential import (
    BasicAuthCredentials,
    generate_random_token,
    hash_token1,
    hash_token256,
    match_token1,
    match_token256,
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


class HashTokenTest(TestCase):

    def test_hash_token1(self):
        """hash_token returns the SHA1 hash of the specified string."""
        self.assertEqual(
            '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33', hash_token1('foo'))

        def test_hash_token256(self):
            """hash_token returns the SHA256 hash of the specified string."""
            self.assertEqual(
                '2c26b46b68ffc68ff99b453c1d3041'
                '3413422d706483bfa0f98a5e886266e7ae', hash_token256('foo'))


class MatchTokenTest(TestCase):

    def test_token_matches1(self):
        """match_token returns True if the token matches the SHA1 hash."""
        self.assertTrue(
            match_token1('foo', '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33'))

    def test_token_no_match1(self):
        """match_token returns False if the token doesn't match the hash."""
        self.assertFalse(match_token1('foo', 'wronghashsum'))

    def test_token_matches256(self):
        """match_token returns True if the token matches the SHA1 hash."""
        self.assertTrue(
            match_token256(
                'foo',
                '2c26b46b68ffc68ff99b453c1d3041341'
                '3422d706483bfa0f98a5e886266e7ae'))

    def test_token_no_match256(self):
        """match_token returns False if the token doesn't match the hash."""
        self.assertFalse(match_token256('foo', 'wronghashsum'))
