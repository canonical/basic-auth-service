"""Database schema definitions."""

from sqlalchemy import (
    Column,
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


API_CREDENTIALS = Table(
    'api_credentials',
    METADATA,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False, unique=True),
    Column('password', String, nullable=False),
    Column('description', String, nullable=True),
)
