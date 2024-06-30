"""empty message

Revision ID: 784edcf8ceda
Revises: dea1d92ddd45
Create Date: 2024-06-30 11:56:16.546502

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '784edcf8ceda'
down_revision = 'dea1d92ddd45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order')
    op.drop_table('profile')
    op.drop_table('cart')
    op.drop_table('payment')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('address')
        batch_op.drop_column('date_of_birth')
        batch_op.drop_column('name')

    op.create_table('payment',
    sa.Column('payment_id', sa.BIGINT(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('account_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('payment_method', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('payment_status', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('payment_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('payment_id', name='payment_pkey')
    )
    op.create_table('cart',
    sa.Column('cart_id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), autoincrement=True, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('account_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('quantity', sa.SMALLINT(), autoincrement=False, nullable=True),
    sa.Column('cart_item_price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('cart_id', name='cart_pkey')
    )
    op.create_table('profile',
    sa.Column('profile_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('date_of_birth', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='profile_user_id_fkey'),
    sa.PrimaryKeyConstraint('profile_id', name='profile_pkey')
    )
    op.create_table('order',
    sa.Column('order_id', sa.BIGINT(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), autoincrement=True, nullable=False),
    sa.Column('account_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('order_status', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('order_price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('order_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('product_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('quantity', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('order_id', name='order_pkey')
    )
    # ### end Alembic commands ###
