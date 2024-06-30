"""empty message

Revision ID: 0a28db524652
Revises: b30e02e3e882
Create Date: 2024-06-30 15:40:41.205785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a28db524652'
down_revision = 'b30e02e3e882'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sessions',
    sa.Column('ssid', sa.String(length=255), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=255), nullable=True),
    sa.Column('referer', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('ssid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    # ### end Alembic commands ###
