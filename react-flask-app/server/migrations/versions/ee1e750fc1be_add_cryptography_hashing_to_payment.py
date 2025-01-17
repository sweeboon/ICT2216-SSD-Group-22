"""Add cryptography hashing to payment

Revision ID: ee1e750fc1be
Revises: dcb51cb4503a
Create Date: 2024-07-07 23:17:45.862185

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ee1e750fc1be'
down_revision = 'dcb51cb4503a'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.alter_column('credit_card_number',
                              existing_type=sa.String(length=255),
                              type_=sa.LargeBinary(),
                              existing_nullable=True,
                              postgresql_using='credit_card_number::bytea')
        batch_op.alter_column('expiry_date',
                              existing_type=sa.String(length=255),
                              type_=sa.LargeBinary(),
                              existing_nullable=True,
                              postgresql_using='expiry_date::bytea')
        batch_op.alter_column('cvv',
                              existing_type=sa.String(length=255),
                              type_=sa.LargeBinary(),
                              existing_nullable=True,
                              postgresql_using='cvv::bytea')

def downgrade():
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.alter_column('credit_card_number',
                              existing_type=sa.LargeBinary(),
                              type_=sa.String(length=128),
                              existing_nullable=True,
                              postgresql_using='credit_card_number::text')
        batch_op.alter_column('expiry_date',
                              existing_type=sa.LargeBinary(),
                              type_=sa.String(length=128),
                              existing_nullable=True,
                              postgresql_using='expiry_date::text')
        batch_op.alter_column('cvv',
                              existing_type=sa.LargeBinary(),
                              type_=sa.String(length=128),
                              existing_nullable=True,
                              postgresql_using='cvv::text')
