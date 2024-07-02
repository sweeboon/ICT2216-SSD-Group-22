"""empty message

Revision ID: edfa0dcdc961
Revises: 2f76a4c05172
Create Date: 2024-07-01 08:02:21.164333

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'edfa0dcdc961'
down_revision = '2f76a4c05172'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('confirmed_on', sa.DateTime(), nullable=True),
    sa.Column('otp', sa.String(length=6), nullable=True),
    sa.Column('otp_generated_at', sa.DateTime(), nullable=True),
    sa.Column('new_email', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('twofa_enabled', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('account_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('roles_accounts',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.account_id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('account_id', 'role_id')
    )
    op.drop_table('roles_users')
    op.drop_table('user')
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_constraint('cart_product_id_fkey', type_='foreignkey')
        batch_op.drop_column('product_id')
        batch_op.drop_column('account_id')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('payment_id')
        batch_op.drop_column('product_id')
        batch_op.drop_column('account_id')

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_column('account_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=True))

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('payment_id', sa.INTEGER(), autoincrement=False, nullable=True))

    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('cart_product_id_fkey', 'product', ['product_id'], ['product_id'])

    op.create_table('user',
    sa.Column('user_id', sa.INTEGER(), server_default=sa.text("nextval('user_user_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_login_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('login_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('confirmed', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('confirmed_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('otp', sa.VARCHAR(length=6), autoincrement=False, nullable=True),
    sa.Column('otp_generated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('new_email', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('date_of_birth', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('twofa_enabled', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('user_id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('role_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='roles_users_role_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='roles_users_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'role_id', name='roles_users_pkey')
    )
    op.drop_table('roles_accounts')
    op.drop_table('account')
    # ### end Alembic commands ###