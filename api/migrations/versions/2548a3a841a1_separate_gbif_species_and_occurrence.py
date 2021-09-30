"""separate gbif species and occurrence

Revision ID: 2548a3a841a1
Revises: 4420116fa319
Create Date: 2021-09-30 09:12:32.864080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2548a3a841a1'
down_revision = '4420116fa319'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('queue')
    op.alter_column('scan', 'gbif_id', new_column_name='gbif_species_id', existing_type=sa.Integer)
    op.add_column('scan', sa.Column('gbif_occurrence_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('scan', 'gbif_species_id', new_column_name='gbif_id', existing_type=sa.Integer)
    op.drop_column('scan', 'gbif_occurrence_id')
    op.create_table('queue',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('method', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('arguments', mysql.JSON(), nullable=True),
    sa.Column('created', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
