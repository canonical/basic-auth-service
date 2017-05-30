"""Hash API passwords.

Revision ID: 2
Revises: 1
Create Date: 2017-05-30 07:28:55.609743

"""

import hashlib

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2'
down_revision = '1'
branch_labels = None
depends_on = None


API_CREDENTIALS = sa.Table(
    'api_credentials',
    sa.MetaData(),
    sa.Column('id', sa.Integer),
    sa.Column('password', sa.String),
)


def sha1sum(password):
    return hashlib.sha1(password.encode('utf-8')).hexdigest()


def upgrade():
    conn = op.get_bind()
    result = conn.execute(API_CREDENTIALS.select())
    data = [
        {'_id': row['id'], 'password': sha1sum(row['password'])}
        for row in result.fetchall()]

    if not data:
        return

    conn.execute(
        API_CREDENTIALS.update().where(
            API_CREDENTIALS.c.id == sa.bindparam('_id')).values(
                password=sa.bindparam('password')),
        data)


def downgrade():
    pass
