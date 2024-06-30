"""empty message

Revision ID: 2f76a4c05172
Revises: 908b92483d64
Create Date: 2024-06-30 18:50:38.265128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f76a4c05172'
down_revision = '908b92483d64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.alter_column('product_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key(None, 'product', ['product_id'], ['product_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('product_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###
