"""
Add gbif column to taxonomy.

Revision ID: 8b76ef5c47ef
Revises: 01816b2fcaea
Create Date: 2024-04-05 16:19:09.627686
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b76ef5c47ef'
down_revision = '01816b2fcaea'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('taxonomy', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gbif', sa.Boolean(), nullable=True))

    op.execute("update taxonomy set gbif = 1")
    op.alter_column('taxonomy', 'gbif', nullable=False)


def downgrade():
    with op.batch_alter_table('taxonomy', schema=None) as batch_op:
        batch_op.drop_column('gbif')
