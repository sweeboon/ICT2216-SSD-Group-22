"""empty message

Revision ID: 2de15ae75c14
Revises: 769d45425544
Create Date: 2024-06-26 14:28:26.691227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2de15ae75c14'
down_revision = '769d45425544'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confirmed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('confirmed_on', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('confirmed_on')
        batch_op.drop_column('confirmed')

    # ### end Alembic commands ###
