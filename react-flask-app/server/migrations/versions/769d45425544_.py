"""empty message

Revision ID: 769d45425544
Revises: 310b21ec7f71
Create Date: 2024-06-26 14:12:25.517337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '769d45425544'
down_revision = '310b21ec7f71'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('product_description', sa.String(length=255), nullable=True),
    sa.Column('product_price', sa.Float(), nullable=True),
    sa.Column('stock', sa.Integer(), nullable=True),
    sa.Column('image_path', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.drop_table('Product')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Product',
    sa.Column('product_id', sa.BIGINT(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), autoincrement=True, nullable=False),
    sa.Column('category_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('image_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('product_description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('product_price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('stock', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('image_path', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('product_id', name='Product_pkey'),
    sa.UniqueConstraint('product_id', name='Product_product_id_key')
    )
    op.drop_table('product')
    # ### end Alembic commands ###
