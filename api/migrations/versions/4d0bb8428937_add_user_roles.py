"""empty message

Revision ID: 4d0bb8428937
Revises: 1aa4435fb125
Create Date: 2022-09-14 14:59:15.377881

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision = '4d0bb8428937'
down_revision = '1aa4435fb125'
branch_labels = None
depends_on = None


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    role = sa.Column(mysql.ENUM('USER', 'CONTRIBUTOR', 'ADMIN'))


class UserRole(Base):
    __tablename__ = 'roles_users'
    user_id = sa.Column(sa.Integer(), primary_key=True)
    role_id = sa.Column(sa.Integer(), primary_key=True)


class Role(Base):
    __tablename__ = 'role'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=80))
    priority = sa.Column(sa.Integer)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    role_table = op.create_table('role',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=80), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('priority', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.bulk_insert(role_table, [
        {'id': 1, 'name': 'ADMIN', 'description': 'Site administrator', 'priority': 1},
        {'id': 2, 'name': 'CONTRIBUTOR', 'description': 'Content contributor', 'priority': 2},
        {'id': 3, 'name': 'USER', 'description': 'Basic user'},
    ], multiinsert=False)

    roles_users_table = op.create_table('roles_users',
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
                    )

    bind = op.get_bind()
    session = orm.Session(bind=bind)
    user_roles = []
    role_dict = {
        'ADMIN': 1,
        'CONTRIBUTOR': 2,
        'USER': 3
    }
    for user in session.query(User):
        user_roles.append({'user_id': user.id, 'role_id': role_dict.get(user.role, 3)})
    op.bulk_insert(roles_users_table, user_roles, multiinsert=False)

    op.add_column('user', sa.Column('active', sa.Boolean(), nullable=False, server_default='1'))
    op.drop_column('user', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user',
                  sa.Column('role', mysql.ENUM('USER', 'CONTRIBUTOR', 'ADMIN'), server_default=sa.text("'USER'"),
                            nullable=True))

    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for user in session.query(User):
        highest_role = session.query(UserRole).filter(UserRole.user_id == user.id).join(Role,
                                                                                        UserRole.role_id == Role.id).order_by(
            Role.priority).first()
        if highest_role is None:
            highest_role = 3
        else:
            highest_role = highest_role.role_id
        role_name = session.query(Role).get(highest_role).name
        user.role = role_name
    session.commit()

    op.drop_column('user', 'active')
    op.drop_table('roles_users')
    op.drop_table('role')
    # ### end Alembic commands ###