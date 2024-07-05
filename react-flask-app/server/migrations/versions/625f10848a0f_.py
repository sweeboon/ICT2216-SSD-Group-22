"""empty message

Revision ID: 625f10848a0f
Revises: 8303dee0a59c
Create Date: 2024-07-06 00:00:12.661273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '625f10848a0f'
down_revision = '8303dee0a59c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_price', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_column('product_price')

    # ### end Alembic commands ###