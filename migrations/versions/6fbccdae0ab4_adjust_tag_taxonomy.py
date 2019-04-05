"""adjust tag taxonomy

Revision ID: 6fbccdae0ab4
Revises: f222f8856fa2
Create Date: 2019-04-03 13:34:29.996919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fbccdae0ab4'
down_revision = 'f222f8856fa2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.add_column(sa.Column('taxonomy', sa.String(length=250), nullable=True))
        batch_op.drop_column('parent_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('parent_id', 'tag', ['parent_id'], ['id'])
        batch_op.drop_column('taxonomy')

    # ### end Alembic commands ###