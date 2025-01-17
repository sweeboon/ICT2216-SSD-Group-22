"""empty message

Revision ID: cf2975fbab4b
Revises: edfa0dcdc961
Create Date: 2024-07-01 08:03:36.804853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf2975fbab4b'
down_revision = 'edfa0dcdc961'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'account', ['account_id'], ['account_id'])
        batch_op.create_foreign_key(None, 'product', ['product_id'], ['product_id'])

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('product_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'payment', ['payment_id'], ['payment_id'])
        batch_op.create_foreign_key(None, 'product', ['product_id'], ['product_id'])
        batch_op.create_foreign_key(None, 'account', ['account_id'], ['account_id'])

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'account', ['account_id'], ['account_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('account_id')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('product_id')
        batch_op.drop_column('account_id')
        batch_op.drop_column('payment_id')

    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('account_id')
        batch_op.drop_column('product_id')

    # ### end Alembic commands ###
