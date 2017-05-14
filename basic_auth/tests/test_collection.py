import asynctest

from ..collection import CredentialsCollection
from ..api.error import InvalidResourceDetails


class CredentialsCollectionTest(asynctest.TestCase):

    def setUp(self):
        super().setUp()
        self.collection = CredentialsCollection()

    async def test_missing_user(self):
        """If the "user" parameter is not provided, an error is raised."""
        with self.assertRaises(InvalidResourceDetails):
            await self.collection.create({'token': 'foo:bar'})

    async def test_create_with_token(self):
        """If token is not None, it's saved."""
        details = {'user': 'foo', 'token': 'foo:bar'}
        await self.collection.create(details)
        self.assertEqual(details, await self.collection.get('foo'))

    async def test_create_random_token(self):
        """If token is None, one is generated."""
        await self.collection.create({'user': 'foo', 'token': None})
        details = await self.collection.get('foo')
        self.assertIsNotNone(details['token'])
        result = await self.collection.get('foo')
        self.assertIsNotNone(result['token'])

    async def test_update_with_token(self):
        """If token is Not none, the updated one is saved."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        await self.collection.update('foo', {'token': 'new:token'})
        details = await self.collection.get('foo')
        self.assertEqual('new:token', details['token'])

    async def test_update_random_token(self):
        """If token is None, it's updated to a random one."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        await self.collection.update('foo', {'token': None})
        details = await self.collection.get('foo')
        self.assertIsNotNone(details['token'])
        self.assertNotEqual('foo:bar', details['token'])

    async def test_credentials_match_true(self):
        """credentials_match returns True if given credentials match."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.assertTrue(await self.collection.credentials_match('foo', 'bar'))

    async def test_credentials_match_false(self):
        """credentials_match returns False if no match is found."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.assertFalse(await self.collection.credentials_match('foo', 'baz'))
        self.assertFalse(await self.collection.credentials_match('baz', 'bar'))
