"""Add creation_time timestamps

Revision ID: 3
Revises: 2
Create Date: 2018-04-30

"""
from alembic import op
from sqlalchemy import (
    Column,
    DateTime,
    func,
)


# revision identifiers, used by Alembic.
revision = '3'
down_revision = '2'
branch_labels = None
depends_on = None


EPOCH = '1970-01-01 00:00:00+00'


def add_creation_time(table_name):
    op.add_column(
        table_name,
        Column("creation_time", DateTime, default=func.now()))
    op.execute(
        "UPDATE %s SET creation_time='%s' WHERE creation_time IS NULL"
        % (table_name, EPOCH))
    op.alter_column(table_name, 'creation_time', nullable=False)


def upgrade():
    add_creation_time('api_credentials')
    add_creation_time('credentials')


def downgrade():
    op.drop_column('api_credentials', 'creation_time')
    op.drop_column('credentials', 'creation_time')
