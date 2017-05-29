"""Database models."""

from collections import namedtuple

from ..credential import (
    BasicAuthCredentials,
    hash_token,
    match_token,
)
from .schema import (
    CREDENTIALS,
    API_CREDENTIALS,
)


# Database fields
CREDENTIALS_FIELDS = ('user', 'username', 'password')
API_CREDENTIALS_FIELDS = ('username', 'password', 'description')

Credentials = namedtuple('Credentials', ('user', 'auth'))
APICredentials = namedtuple('APICredentials', API_CREDENTIALS_FIELDS)


class HashedAPICredentials(APICredentials):
    """API credentials where the password is hashed."""

    def password_match(self, password):
        """Return whether the password matches the hashed one."""
        return match_token(password, self.password)


class Model:
    """The database model."""

    def __init__(self, conn):
        self._conn = conn

    async def add_credentials(self, user, username, password):
        """Add user credentials."""
        await self._conn.execute(
            CREDENTIALS.insert().values(
                user=user, username=username, password=password))
        return Credentials(user, BasicAuthCredentials(username, password))

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
        result = await self._conn.execute(
            CREDENTIALS.update().where(CREDENTIALS.c.user == user).values(
                username=username, password=password))
        return bool(result.rowcount)

    async def is_known_user(self, user):
        """Return whether credentials exist for the specified user."""
        query = CREDENTIALS.select().where(
            CREDENTIALS.c.user == user)
        result = await self._conn.execute(query)
        return bool(result.rowcount)

    async def remove_credentials(self, user):
        """Remove credentials for the specified user."""
        query = CREDENTIALS.delete().where(CREDENTIALS.c.user == user)
        result = await self._conn.execute(query)
        return bool(result.rowcount)

    async def add_api_credentials(self, username, password, description=None):
        """Add credentials for an API user."""
        if description is None:
            description = ''
        await self._conn.execute(
            API_CREDENTIALS.insert().values(
                username=username, password=hash_token(password),
                description=description))
        return APICredentials(username, password, description)

    async def get_api_credentials(self, username):
        """Return credentials for an API user."""
        result = await self._conn.execute(
            API_CREDENTIALS.select().where(
                API_CREDENTIALS.c.username == username))
        row = await result.fetchone()
        if row is not None:
            return HashedAPICredentials(
                row['username'], row['password'], row['description'])

    async def remove_api_credentials(self, username):
        """Remove credentials for an API user."""
        query = API_CREDENTIALS.delete().where(
            API_CREDENTIALS.c.username == username)
        result = await self._conn.execute(query)
        return bool(result.rowcount)

    async def get_all_api_credentials(self):
        """Return all API credentials."""
        result = await self._conn.execute(
            API_CREDENTIALS.select().order_by(API_CREDENTIALS.c.username))
        return [
            HashedAPICredentials(
                row['username'], row['password'], row['description'])
            for row in await result.fetchall()]
