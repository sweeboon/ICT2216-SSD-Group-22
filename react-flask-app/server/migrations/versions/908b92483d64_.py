"""empty message

Revision ID: 908b92483d64
Revises: 90f7934697ac
Create Date: 2024-06-30 18:37:46.558446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '908b92483d64'
down_revision = '90f7934697ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_column('session_id')

    # ### end Alembic commands ###
