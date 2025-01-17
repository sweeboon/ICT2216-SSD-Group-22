"""empty message

Revision ID: dea1d92ddd45
Revises: ec7bc093acc0
Create Date: 2024-06-29 20:25:57.411440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dea1d92ddd45'
down_revision = 'ec7bc093acc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('otp', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('otp_generated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('new_email', sa.String(length=255), nullable=True))
        batch_op.drop_column('date_of_birth')
        batch_op.drop_column('address')
        batch_op.drop_column('name')
        batch_op.drop_column('role')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('name', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('address', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('date_of_birth', sa.DATE(), autoincrement=False, nullable=True))
        batch_op.drop_column('new_email')
        batch_op.drop_column('otp_generated_at')
        batch_op.drop_column('otp')

    # ### end Alembic commands ###
