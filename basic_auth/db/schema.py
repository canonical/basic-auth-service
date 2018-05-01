"""Database schema definitions."""

from sqlalchemy import (
    Column,
    DateTime,
    func,
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
    Column("creation_time", DateTime, default=func.now(), nullable=False),
)


API_CREDENTIALS = Table(
    'api_credentials',
    METADATA,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False, unique=True),
    Column('password', String, nullable=False),
    Column('description', String, nullable=False, server_default='',
           default=''),
    Column("creation_time", DateTime, default=func.now(), nullable=False),
)
