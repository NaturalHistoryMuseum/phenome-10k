"""
set gbif id types to bigint.

Revision ID: 1aa4435fb125
Revises: 2548a3a841a1
Create Date: 2021-11-16 11:05:37.235084
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1aa4435fb125'
down_revision = '2548a3a841a1'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'scan', 'gbif_species_id', type_=sa.BigInteger, existing_type=sa.Integer
    )
    op.alter_column(
        'scan', 'gbif_occurrence_id', type_=sa.BigInteger, existing_type=sa.Integer
    )


def downgrade():
    op.alter_column(
        'scan', 'gbif_species_id', type_=sa.Integer, existing_type=sa.BigInteger
    )
    op.alter_column(
        'scan', 'gbif_occurrence_id', type_=sa.Integer, existing_type=sa.BigInteger
    )
