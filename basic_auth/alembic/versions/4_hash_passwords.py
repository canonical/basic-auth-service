"""Hash API passwords.

Revision ID: 4
Revises: 3
Create Date: 201-05-30 07:28:55.609743

"""

import hashlib

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4'
down_revision = '3'
branch_labels = None
depends_on = None


CREDENTIALS = sa.Table(
    'credentials',
    sa.MetaData(),
    sa.Column('id', sa.Integer),
    sa.Column('password', sa.String),
)


def sha256sum(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def upgrade():
    conn = op.get_bind()
    result = conn.execute(CREDENTIALS.select())
    data = [
        {'_id': row['id'], 'password': sha256sum(row['password'])}
        for row in result.fetchall()]

    if not data:
        return

    conn.execute(
        CREDENTIALS.update().where(
            CREDENTIALS.c.id == sa.bindparam('_id')).values(
                password=sa.bindparam('password')),
        data)


def downgrade():
    """Downgrade is not possible by the nature of hashing."""
    pass
