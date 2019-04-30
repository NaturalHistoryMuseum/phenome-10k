"""Redefine relationship with attachments

Revision ID: 6ab07e63e2a9
Revises: c240994711dd
Create Date: 2019-04-29 16:51:39.911717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ab07e63e2a9'
down_revision = 'c240994711dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('publication_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('attachment_id', 'attachment', ['attachment_id'], ['id'])
        batch_op.drop_column('file_id')

    with op.batch_alter_table('scan_attachment', schema=None) as batch_op:
        batch_op.create_foreign_key('attachment_id', 'attachment', ['attachment_id'], ['id'])
        batch_op.drop_column('file_id')
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('scan_attachment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=250), nullable=False))
        batch_op.add_column(sa.Column('file_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'file', ['file_id'], ['id'])

    with op.batch_alter_table('publication_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_id', sa.INTEGER(), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'file', ['file_id'], ['id'])
        batch_op.drop_column('id')

    # ### end Alembic commands ###