from ..testing import DataBaseTest

from ..model import Model


class ModelTest(DataBaseTest):

    async def setUp(self):
        await super().setUp()
        self.model = Model(self.conn)

    async def test_add_credentials(self):
        """Credentials for a user can be added."""
        await self.model.add_credentials('user', 'username', 'pass')
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

    async def test_remove(self):
        """Credentials can be removed."""
        await self.model.add_credentials('user', 'username', 'pass')
        await self.model.remove_credentials('user')
        self.assertIsNone(await self.model.get_credentials(user='user'))

    async def test_remove_not_found(self):
        """Removal doesn't fail if the user is not found."""
        self.assertIsNone(await self.model.remove_credentials('user'))

    async def test_is_known_user_false(self):
        """is_known_user returns False if the user is not found."""
        await self.model.add_credentials('user', 'username', 'pass')
        self.assertFalse(await self.model.is_known_user('another'))

    async def test_is_known_user_true(self):
        """is_known_user returns True if the user exists."""
        await self.model.add_credentials('user', 'username', 'pass')
        self.assertTrue(await self.model.is_known_user('user'))
