"""Database models."""

from collections import namedtuple

from ..credential import BasicAuthCredentials
from .schema import CREDENTIALS


# Database fields
CREDENTIALS_FIELDS = ('user', 'username', 'password')

Credentials = namedtuple('Credentials', ['user', 'auth'])


class Model:
    """The database model."""

    def __init__(self, conn):
        self._conn = conn

    async def add_credentials(self, user, username, password):
        """Add user credentials."""
        await self._conn.execute(
            CREDENTIALS.insert().values(
                user=user, username=username, password=password))

    async def get_credentials(self, user=None, username=None):
        """Return credentials by user or username."""
        if (user, username) == (None, None):
            raise RuntimeError('Need to pass user or username')

        query = CREDENTIALS.select()
        if user:
            query = query.where(CREDENTIALS.c.user == user)
        if username:
            query = query.where(CREDENTIALS.c.username == username)

        result = await self._conn.execute(query)
        row = await result.fetchone()
        if row is None:
            return

        return Credentials(
            row['user'],
            BasicAuthCredentials(row['username'], row['password']))

    async def update_credentials(self, user, username, password):
        """Update user credentials."""
        await self._conn.execute(
            CREDENTIALS.update().where(CREDENTIALS.c.user == user).values(
                username=username, password=password))

    async def is_known_user(self, user):
        """Return whether credentials exist for the specified user."""
        query = CREDENTIALS.select().where(
            CREDENTIALS.c.user == user)
        result = await self._conn.execute(query)
        return bool(result.rowcount)

    async def remove_credentials(self, user):
        """Remove credentials for the specified user."""
        query = CREDENTIALS.delete().where(CREDENTIALS.c.user == user)
        await self._conn.execute(query)
