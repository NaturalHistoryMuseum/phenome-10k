from flask_login import UserMixin
from passlib.context import CryptContext
from phenome10k.extensions import db, login
from sqlalchemy.sql import func


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Allow decoding phpasswords, but deprecate all but argon2
crypt_ctx = CryptContext(
    schemes=['argon2', 'phpass'],
    deprecated=['auto']
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    date_registered = db.Column(db.DateTime(), server_default=func.now())
    role = db.Column(db.Enum('USER', 'CONTRIBUTOR', 'ADMIN'), server_default='USER')
    country_code = db.Column(db.String(2))
    user_type = db.Column(db.String(64))

    scans = db.relationship('Scan', backref='author')

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_contributor(self):
        return self.is_admin() or self.role == 'CONTRIBUTOR'

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
            'role': self.role,
            'country_code': self.country_code,
            'user_type': self.user_type
        }
