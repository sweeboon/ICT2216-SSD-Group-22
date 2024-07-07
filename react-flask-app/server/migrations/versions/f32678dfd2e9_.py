"""empty message

Revision ID: f32678dfd2e9
Revises: c056e5431232
Create Date: 2024-07-07 20:46:07.077972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f32678dfd2e9'
down_revision = 'c056e5431232'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ip_address', sa.String(length=45), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.drop_column('ip_address')

    # ### end Alembic commands ###
