"""Add user uniquifier

Revision ID: 2c7579ef30d0
Revises: 4d0bb8428937
Create Date: 2022-09-15 11:32:16.114156

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import uuid


# revision identifiers, used by Alembic.
revision = '2c7579ef30d0'
down_revision = '4d0bb8428937'
branch_labels = None
depends_on = None


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    fs_uniquifier = sa.Column(sa.String(255))


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('fs_uniquifier', sa.String(length=255), nullable=False, server_default=''))
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for user in session.query(User):
        user.fs_uniquifier = uuid.uuid4().hex
    session.commit()
    op.create_unique_constraint(None, 'user', ['fs_uniquifier'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fs_uniquifier', 'user', type_='unique')
    op.drop_column('user', 'fs_uniquifier')
    # ### end Alembic commands ###
