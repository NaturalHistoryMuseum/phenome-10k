"""Add taxonomy table

Revision ID: ee36c2cf4e0b
Revises: 6fbccdae0ab4
Create Date: 2019-04-09 16:29:13.164347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee36c2cf4e0b'
down_revision = '6fbccdae0ab4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('taxonomy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['taxonomy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scan_taxonomy',
    sa.Column('taxonomy_id', sa.Integer(), nullable=False),
    sa.Column('scan_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['scan_id'], ['scan.id'], ),
    sa.ForeignKeyConstraint(['taxonomy_id'], ['taxonomy.id'], ),
    sa.PrimaryKeyConstraint('taxonomy_id', 'scan_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scan_taxonomy')
    op.drop_table('taxonomy')
    # ### end Alembic commands ###
