"""Database schema definitions."""

from sqlalchemy import (
    Column,
    Index,
    Integer,
    MetaData,
    String,
    Table,
)


METADATA = MetaData()


CREDENTIALS = Table(
    'credentials',
    METADATA,
    Column('id', Integer, primary_key=True),
    Column('user', String, nullable=False, unique=True),
    Column('username', String, nullable=False, unique=True),
    Column('password', String, nullable=False),
)

Index('credentials_user_idx', CREDENTIALS.c.user, unique=True)
Index('credentials_username_idx', CREDENTIALS.c.username, unique=True)
