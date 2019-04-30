"""Add generic attachment table

Revision ID: c240994711dd
Revises: 1cdbca4d6453
Create Date: 2019-04-29 16:16:01.107180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c240994711dd'
down_revision = '1cdbca4d6453'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    attachment = op.create_table('attachment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=250), nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('publication_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attachment_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('scan_attachment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attachment_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('scan_attachment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=250), nullable=False))
        batch_op.add_column(sa.Column('file_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'file', ['file_id'], ['id'])
        batch_op.drop_column('attachment_id')

    with op.batch_alter_table('publication_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_id', sa.INTEGER(), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'file', ['file_id'], ['id'])
        batch_op.drop_column('id')
        batch_op.drop_column('attachment_id')

    op.drop_table('attachment')
    # ### end Alembic commands ###