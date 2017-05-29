import unittest

from ..testing import DataBaseTest

from ..model import (
    Model,
    HashedAPICredentials,
)
from ...credential import hash_token


class HashedAPICredentialsTest(unittest.TestCase):

    def test_password_match_true(self):
        """password_match returns True if the password matches."""
        credentials = HashedAPICredentials(
            'user', hash_token('pass'), 'a user')
        self.assertTrue(credentials.password_match('pass'))

    def test_password_match_false(self):
        """password_match returns false if the password doesn't match."""
        credentials = HashedAPICredentials(
            'user', hash_token('pass'), 'a user')
        self.assertFalse(credentials.password_match('other password'))


class ModelTest(DataBaseTest):

    async def setUp(self):
        await super().setUp()
        self.model = Model(self.conn)

    async def test_add_credentials(self):
        """Credentials for a user can be added."""
        result = await self.model.add_credentials(
            'user', 'username', 'pass')
        self.assertEqual('user', result.user)
        self.assertEqual('username', result.auth.username)
        self.assertEqual('pass', result.auth.password)
        credentials = await self.model.get_credentials(user='user')
        self.assertEqual('user', credentials.user)
        self.assertEqual('username', credentials.auth.username)
        self.assertEqual('pass', credentials.auth.password)

    async def test_get_credentials_by_user(self):
        """Credentials for a user can be retrieved by user."""
        await self.model.add_credentials('user', 'username', 'pass')
        credentials = await self.model.get_credentials(user='user')
        self.assertEqual('user', credentials.user)

    async def test_get_credentials_by_username(self):
        """Credentials for a user can be retrieved by user."""
        await self.model.add_credentials('user', 'username', 'pass')
        credentials = await self.model.get_credentials(username='username')
        self.assertEqual('user', credentials.user)

    async def test_get_credentials_not_found(self):
        """If credentials for the user are not found, None is returned."""
        self.assertIsNone(await self.model.get_credentials(user='user'))

    async def test_get_credentials_user_or_username(self):
        """Either the user or the username must be specified.."""
        with self.assertRaises(RuntimeError) as cm:
            await self.model.get_credentials()
        self.assertEqual('Need to pass user or username', str(cm.exception))

    async def test_remove_credentials(self):
        """Credentials can be removed."""
        await self.model.add_credentials('user', 'username', 'pass')
        removed = await self.model.remove_credentials('user')
        self.assertTrue(removed)
        self.assertIsNone(await self.model.get_credentials(user='user'))

    async def test_remove_credentials_not_found(self):
        """If the user is not found, remove_credentials returns False."""
        self.assertFalse(await self.model.remove_credentials('user'))

    async def test_update_credentials(self):
        """Credentials can be updated."""
        await self.model.add_credentials('user', 'username', 'pass')
        updated = await self.model.update_credentials(
            'user', 'newusername', 'newpass')
        self.assertTrue(updated)
        credentials = await self.model.get_credentials(user='user')
        self.assertEqual('user', credentials.user)
        self.assertEqual('newusername', credentials.auth.username)
        self.assertEqual('newpass', credentials.auth.password)

    async def test_update_credentials_not_found(self):
        """If the user is not found, update_credentials returns False."""
        updated = await self.model.update_credentials(
            'user', 'newusername', 'newpass')
        self.assertFalse(updated)

    async def test_is_known_user_false(self):
        """is_known_user returns False if the user is not found."""
        await self.model.add_credentials('user', 'username', 'pass')
        self.assertFalse(await self.model.is_known_user('another'))

    async def test_is_known_user_true(self):
        """is_known_user returns True if the user exists."""
        await self.model.add_credentials('user', 'username', 'pass')
        self.assertTrue(await self.model.is_known_user('user'))

    async def test_add_api_credentials(self):
        """Credentials for an API user can be added."""
        result = await self.model.add_api_credentials('username', 'pass')
        self.assertEqual('username', result.username)
        self.assertEqual('pass', result.password)
        self.assertEqual('', result.description)
        credentials = await self.model.get_api_credentials('username')
        self.assertEqual('username', credentials.username)
        self.assertTrue(credentials.password_match('pass'))
        self.assertEqual('', credentials.description)

    async def test_add_api_credentials_with_description(self):
        """A description can be added for API user credentials."""
        result = await self.model.add_api_credentials(
            'username', 'pass', description='a user')
        self.assertEqual('a user', result.description)
        credentials = await self.model.get_api_credentials('username')
        self.assertEqual('a user', credentials.description)

    async def test_add_api_credentials_with_description_none(self):
        """If description is None, it's saved as empty string."""
        await self.model.add_api_credentials(
            'username', 'pass', description=None)
        credentials = await self.model.get_api_credentials('username')
        self.assertEqual('', credentials.description)

    async def test_get_api_credentials(self):
        """Credentials for an API user can be retrieved."""
        await self.model.add_api_credentials('username', 'pass')
        await self.model.add_api_credentials('username2', 'pass2')
        credentials = await self.model.get_api_credentials('username')
        self.assertEqual('username', credentials.username)
        self.assertTrue(credentials.password_match('pass'))
        self.assertEqual('', credentials.description)

    async def test_remove_api_credentials(self):
        """API user credentials can be removed."""
        await self.model.add_api_credentials('username', 'pass')
        removed = await self.model.remove_api_credentials('username')
        self.assertTrue(removed)
        self.assertIsNone(await self.model.get_api_credentials('username'))

    async def test_remove_api_credentials_not_found(self):
        """If username is unknown, remove_api_credentials returns False."""
        self.assertFalse(await self.model.remove_api_credentials('username'))

    async def test_get_all_api_credentials(self):
        """It's possible to get all API credentials."""
        await self.model.add_api_credentials('username1', 'pass1')
        await self.model.add_api_credentials(
            'username2', 'pass2', description='second user')
        cred1, cred2 = await self.model.get_all_api_credentials()
        self.assertEqual('username1', cred1.username)
        self.assertTrue(cred1.password_match('pass1'))
        self.assertEqual('', cred1.description)
        self.assertEqual('username2', cred2.username)
        self.assertTrue(cred2.password_match('pass2'))
        self.assertEqual('second user', cred2.description)
