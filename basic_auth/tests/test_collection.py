from unittest import TestCase

from ..collection import CredentialsCollection
from ..api.error import InvalidResourceDetails


class CredentialsCollectionTest(TestCase):

    def setUp(self):
        super().setUp()
        self.collection = CredentialsCollection()

    def test_missing_user(self):
        """If the "user" parameter is not provided, an error is raised."""
        self.assertRaises(
            InvalidResourceDetails, self.collection.create,
            {'token': 'foo:bar'})

    def test_create_with_token(self):
        """If token is not None, it's saved."""
        details = {'user': 'foo', 'token': 'foo:bar'}
        self.collection.create(details)
        self.assertEqual(details, self.collection.get('foo'))

    def test_create_random_token(self):
        """If token is None, one is generated."""
        self.collection.create({'user': 'foo', 'token': None})
        details = self.collection.get('foo')
        self.assertIsNotNone(details['token'])
        self.assertIsNotNone(self.collection.get('foo')['token'])

    def test_update_with_token(self):
        """If token is Not none, the updated one is saved."""
        self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.collection.update('foo', {'token': 'new:token'})
        details = self.collection.get('foo')
        self.assertEqual('new:token', details['token'])

    def test_update_random_token(self):
        """If token is None, it's updated to a random one."""
        self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.collection.update('foo', {'token': None})
        details = self.collection.get('foo')
        self.assertIsNotNone(details['token'])
        self.assertNotEqual('foo:bar', details['token'])

    def test_credentials_match_true(self):
        """credentials_match returns True if given credentials match."""
        self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.assertTrue(self.collection.credentials_match('foo', 'bar'))

    def test_credentials_match_false(self):
        """credentials_match returns False if no match is found."""
        self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.assertFalse(self.collection.credentials_match('foo', 'baz'))
        self.assertFalse(self.collection.credentials_match('baz', 'bar'))
