"""
Add confirmation time to user.

Revision ID: 77f6b43f2bfa
Revises: 2c7579ef30d0
Create Date: 2022-09-21 10:47:40.439190
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision = '77f6b43f2bfa'
down_revision = '2c7579ef30d0'
branch_labels = None
depends_on = None


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    date_registered = sa.Column(sa.DateTime())
    confirmed_at = sa.Column(sa.DateTime())


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('confirmed_at', sa.DateTime(), nullable=True))
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for user in session.query(User):
        user.confirmed_at = user.date_registered
    session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'confirmed_at')
    # ### end Alembic commands ###
