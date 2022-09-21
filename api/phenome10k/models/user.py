from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from passlib.context import CryptContext
from phenome10k.extensions import db
from sqlalchemy.sql import func

# Allow decoding phpasswords, but deprecate all but argon2
crypt_ctx = CryptContext(
    schemes=['argon2', 'phpass'],
    deprecated=['auto']
)

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    priority = db.Column(db.Integer())


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    date_registered = db.Column(db.DateTime(), server_default=func.now())
    country_code = db.Column(db.String(2))
    user_type = db.Column(db.String(64))
    active = db.Column(db.Boolean(), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime(), nullable=True)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    scans = db.relationship('Scan', backref='author')

    @property
    def highest_role(self):
        highest_role = db.session.query(roles_users).filter_by(user_id=self.id).join(Role).order_by(Role.priority).first()
        if highest_role is None:
            return None
        return Role.query.get(highest_role.role_id)

    def is_admin(self):
        return 'ADMIN' in self.roles

    def is_contributor(self):
        return 'CONTRIBUTOR' in self.roles

    def can_contribute(self):
        return self.is_admin() or self.is_contributor()

    def set_password(self, password):
        self.password = crypt_ctx.hash(password)

    def check_password(self, password):
        return crypt_ctx.verify(password, self.password)

    def password_needs_update(self):
        return crypt_ctx.needs_update(self.password)

    def check_and_migrate_password(self, password):
        if self.check_password(password):
            if self.password_needs_update():
                self.set_password(password)
            return True
        return False

    def can_edit(self, item):
        """ Returns true if the user can edit the given model """
        return self.is_admin() or item.is_owned_by(self)

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'date_registered': self.date_registered.isoformat(),
            'admin': self.is_admin(),
            'contributor': self.is_contributor(),
            'country_code': self.country_code,
            'user_type': self.user_type
        }


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
