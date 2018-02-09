import asynctest

from ..collection import (
    MemoryCredentialsCollection,
    DataBaseCredentialsCollection,
)
from ..api.error import (
    InvalidResourceDetails,
    ResourceAlreadyExists,
    ResourceNotFound,
)
from ..db import Model
from ..db.testing import DataBaseTest


class CredentialsCollectionTest:
    """Test for all Credentials collections."""

    async def test_create_with_token(self):
        """If token is not None, it's saved."""
        details = {'user': 'foo', 'token': 'foo:bar'}
        with asynctest.mock.patch('logging') as mock_log:
            await self.collection.create(details)
        self.assertEqual(mock_log.info.called_once, True)
        self.assertEqual(details, await self.collection.get('foo'))

    async def test_create_random_token(self):
        """If token is None, one is generated."""
        await self.collection.create({'user': 'foo', 'token': None})
        details = await self.collection.get('foo')
        self.assertIsNotNone(details['token'])

    async def test_create_user_exists(self):
        """If the user already exists, an error is raised."""
        await self.collection.create({'user': 'foo', 'token': None})
        with self.assertRaises(ResourceAlreadyExists):
            await self.collection.create({'user': 'foo', 'token': None})

    async def test_create_username_exists(self):
        """If the username is already in use, an error is raised."""
        await self.collection.create({'user': 'user1', 'token': 'bar:baz'})
        with self.assertRaises(InvalidResourceDetails) as cm:
            await self.collection.create({'user': 'user2', 'token': 'bar:bza'})
        self.assertEqual('Token username already in use', str(cm.exception))

    async def test_delete(self):
        """Credentials for a user can be deleted."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        await self.collection.delete('foo')
        with self.assertRaises(ResourceNotFound):
            await self.collection.get('foo')

    async def test_delete_user_not_found(self):
        """If the user is not known, an error is raised."""
        with self.assertRaises(ResourceNotFound):
            await self.collection.delete('foo')

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

    async def test_update_user_not_found(self):
        """If the user is not known, an error is raised."""
        with self.assertRaises(ResourceNotFound):
            await self.collection.update('foo', {'token': None})

    async def test_update_username_exists(self):
        """If the username is already in use, an error is raised."""
        await self.collection.create({'user': 'user1', 'token': 'bar:baz'})
        await self.collection.create({'user': 'user2', 'token': 'boo:bar'})
        with self.assertRaises(InvalidResourceDetails) as cm:
            await self.collection.update('user2', {'token': 'bar:baa'})
        self.assertEqual('Token username already in use', str(cm.exception))

    async def test_update_username_exists_same_user(self):
        """If the username is used by the same user, no error is raised."""
        await self.collection.create({'user': 'user1', 'token': 'bar:baz'})
        await self.collection.create({'user': 'user2', 'token': 'boo:bar'})
        await self.collection.update('user2', {'token': 'boo:baa'})
        details = await self.collection.get('user2')
        self.assertEqual('boo:baa', details['token'])

    async def test_credentials_match_true(self):
        """credentials_match returns True if given credentials match."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.assertTrue(await self.collection.credentials_match('foo', 'bar'))

    async def test_credentials_match_false(self):
        """credentials_match returns False if no match is found."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        self.assertFalse(await self.collection.credentials_match('foo', 'baz'))
        self.assertFalse(await self.collection.credentials_match('baz', 'bar'))


class MemoryCredentialsCollectionTest(asynctest.TestCase,
                                      CredentialsCollectionTest):

    forbid_get_event_loop = True

    def setUp(self):
        super().setUp()
        self.collection = MemoryCredentialsCollection(self.loop)

    async def test_api_credentials_match_true(self):
        """Test API credentials match."""
        self.assertTrue(
            await self.collection.api_credentials_match('user', 'pass'))

    async def test_api_credentials_match_false(self):
        """Other credentials don't match."""
        self.assertFalse(
            await self.collection.api_credentials_match('foo', 'bar'))


class DataBaseCredentialsCollectionTest(DataBaseTest,
                                        CredentialsCollectionTest):

    async def setUp(self):
        await super().setUp()
        self.model = Model(self.conn)
        self.collection = DataBaseCredentialsCollection(self.engine)

    async def test_rollback_on_error(self):
        """If an error happens in the call, the transaction is aborted."""
        await self.collection.create({'user': 'foo', 'token': 'foo:bar'})
        with self.assertRaises(ValueError):
            await self.collection.update('foo', {'token': 'wrong'})
        details = await self.collection.get('foo')
        # The token is not updated
        self.assertEqual('foo:bar', details['token'])

    async def test_api_credentials_match_true(self):
        """api_credentials_match returns True if API credentials match."""
        await self.model.add_api_credentials('foo', 'bar')
        # need to commit explicitly since collection methods run a separate
        # transaction
        await self.txn.commit()
        self.assertTrue(
            await self.collection.api_credentials_match('foo', 'bar'))

    async def test_api_credentials_match_false(self):
        """api_credentials_match returns False if no match is found."""
        self.assertFalse(
            await self.collection.api_credentials_match('foo', 'bar'))
