from datetime import datetime
from sqlalchemy.sql import func
from app import db, login
from passlib.context import CryptContext
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Allow decoding phpasswords, but deprecate all but argon2
cryptCtx = CryptContext(
    schemes = ['argon2', 'phpass'],
    deprecated = ['auto']
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

    scans = db.relationship('Scan', backref='author', lazy='dynamic')

    def isAdmin(self):
        return self.role == 'ADMIN'

    def isContributor(self):
        return self.isAdmin() or self.role == 'CONTRIBUTOR'

    def setPassword(self, password):
        self.password = cryptCtx.hash(password)

    def checkPassword(self, password):
        return cryptCtx.verify(password, self.password)

    def passwordNeedsUpdate(self):
        return cryptCtx.needs_update(self.password)

    def checkAndMigratePassword(self, password):
        if(self.checkPassword(password)):
            if(self.passwordNeedsUpdate()):
                self.setPassword(password)
            return True
        return False

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gbif_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, index=True, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    scientific_name = db.Column(db.String(250), index=True)
    published = db.Column(db.Boolean)
    url_slug = db.Column(db.String(250), index = True, unique=True)
    alt_name = db.Column(db.String(250))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    specimen_id = db.Column(db.String(250))
    specimen_location = db.Column(db.String(250))
    specimen_link = db.Column(db.String(250))
    description  = db.Column(db.Text())

    file = db.relationship('File')
    publications = db.relationship('Publication', secondary='scan_publication')

    def __repr__(self):
        return '<Scan {}>'.format(self.scientific_name)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    filename = db.Column(db.String(250))
    location = db.Column(db.String(250))
    date_created = db.Column(db.DateTime, index=True, server_default=func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mime_type = db.Column(db.String(250))

    owner = db.relationship('User')

    def __repr__(self):
        return '<File {}>'.format(self.filename)

class PublicationFile(db.Model):
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), primary_key=True)

class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_modified = db.Column(db.DateTime, server_default=func.now())
    title = db.Column(db.String(250))
    published = db.Column(db.Boolean)
    url_slug = db.Column(db.String(250), index=True)
    pub_year = db.Column(db.Integer)
    authors = db.Column(db.String(250))
    journal = db.Column(db.String(250))
    link = db.Column(db.String(250))
    abstract = db.Column(db.Text)

    files = db.relationship('File', secondary='publication_file')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(250))
    name = db.Column(db.String(250))
    parent_id = db.Column(db.Integer, db.ForeignKey('tag.id'))

    parent = db.relationship('Tag')

class ScanPublication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))

class ScanTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))

class ScanAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
