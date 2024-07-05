"""empty message

Revision ID: 648c97d2003a
Revises: 50daff1af7a9
Create Date: 2024-07-06 02:24:06.280995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '648c97d2003a'
down_revision = '50daff1af7a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_column('session_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    op.create_table('sessions',
    sa.Column('ssid', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('token', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('referer', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('ssid', name='sessions_pkey')
    )
    # ### end Alembic commands ###