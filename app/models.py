import magic
import os
import string
import random
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.sql import func
from app import db, login, app
from passlib.context import CryptContext
from flask_login import UserMixin, current_user
from flask.helpers import safe_join
from werkzeug.utils import secure_filename

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

    scans = db.relationship('Scan', backref='author')

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
    ctm_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    specimen_id = db.Column(db.String(250))
    specimen_location = db.Column(db.String(250))
    specimen_link = db.Column(db.String(250))
    description  = db.Column(db.Text())

    source = db.relationship('File', foreign_keys = 'Scan.file_id', cascade="all")
    ctm = db.relationship('File', foreign_keys = 'Scan.ctm_id', cascade="all")
    publications = db.relationship('Publication', secondary='scan_publication', backref='scans')
    attachments = db.relationship('Attachment', secondary='scan_attachment', cascade="all")
    tags = db.relationship('Tag', secondary='scan_tag', lazy='dynamic')
    taxonomy = db.relationship('Taxonomy', secondary='scan_taxonomy')

    errors = []

    @property
    def geologic_age(self):
        return self.tags.filter_by(category='geologic_age').all()

    @property
    def ontogenic_age(self):
        return self.tags.filter_by(category='ontogenic_age').all()

    @property
    def elements(self):
        return self.tags.filter_by(category='elements').all()

    def serialize(self):
        return {
            'id': self.id,
            'type': 'scan',
            'ctm': self.ctm and self.ctm.serialize(),
            'source': self.source and self.source.serialize(),
            'publications': [pub.serialize() for pub in self.publications],
            'attachments': [a.serialize() for a in self.attachments],
            'url_slug': '/' + (self.url_slug if self.url_slug else str(self.id)),
            'thumbnail': len(self.attachments) > 0 and self.attachments[0].file.serialize(),
            'scientific_name': self.scientific_name,
            'gbif_id': self.gbif_id,
            'published': self.published,
            'alt_name': self.alt_name,
            'specimen_id': self.specimen_id,
            'specimen_location': self.specimen_location,
            'specimen_link': self.specimen_link,
            'description': self.description,
            'created': self.date_created.isoformat(),

            'tags': [ tag.serialize() for tag in self.tags ],
            'publications': [ publication.serialize() for publication in self.publications ],
            'stills': [ still.serialize() for still in self.attachments ]
        }

    @staticmethod
    def findBySlug(slug):
        return Scan.query.filter(db.or_(Scan.url_slug == slug, Scan.id == slug)).first()

    def __repr__(self):
        return '<Scan {}>'.format(self.scientific_name)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime, index=True, server_default=func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mime_type = db.Column(db.String(250), nullable=False)
    size = db.Column(db.Integer)

    owner = db.relationship('User')

    @staticmethod
    def fromUpload(fileStorage, save = True):
        """Create a File model from a Werkzeug FileStorage object, and save the file to disk"""
        file = File.fromBinary(fileStorage.filename, fileStorage.stream)
        if save:
            fileStorage.save(file.location)
        return file

    @staticmethod
    def fromBinary(filename, stream):
        """Create a File model from a string filename and file-like object"""
        mimeType = magic.from_buffer(stream.read(1024), mime=True)
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0)

        return File.fromName(
            filename,
            size = size,
            mimeType = mimeType
        )

    @staticmethod
    def fromName(filename, mimeType=None, size=None):
        """Create a File model from a string filename with optional size and mimetype"""

        location = safe_join('uploads', ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + secure_filename(filename))

        return File(
            filename = filename,
            location = location,
            owner_id = current_user.id,
            mime_type = mimeType,
            size = size
        )

    def serialize(self):
        return '/' + self.location

    def __repr__(self):
        return '<File {}>'.format(self.filename)

@event.listens_for(File, 'after_delete')
def receive_after_delete(mapper, connection, target):
    """Ensure the files get deleted from disk when the record is deleted"""
    try:
        os.remove(target.location)
    except:
        pass

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    file = db.relationship(
        'File',
        cascade="all"
    )

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'file': self.file.serialize(),
            'size': self.file.size,
            'filename': self.file.filename
        }

class PublicationFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    publication = db.relationship('Publication')
    attachment = db.relationship('Attachment', cascade='all')


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

    def serialize(self):
        return {
          'id': self.id,
          'type': 'publication',
          'author_id': self.author_id,
        #   'date_created': self.date_created,
        #   'date_modified': self.date_modified,
          'title': self.title,
          'published': self.published,
          'url_slug': self.url_slug,
          'pub_year': self.pub_year,
          'authors': self.authors,
          'journal': self.journal,
          'link': self.link,
          'abstract': self.abstract,
          'files': [ file.serialize() for file in self.files ],
          'scans': [
              {
                  'id': scan.id,
                  'url_slug': scan.url_slug,
                  'scientific_name': scan.scientific_name
              } for scan in self.scans
            ]
        }

    files = db.relationship('Attachment', secondary='publication_file', cascade='all')

    @staticmethod
    def findBySlug(slug):
        return Publication.query.filter(db.or_(Publication.url_slug == slug, Publication.id == slug)).first()

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    taxonomy = db.Column(db.String(250), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    scans = db.relationship('Scan', secondary='scan_tag')

    @property
    def children(self):
        return Tag.query.filter(db.and_(Tag.parent_id==self.id, Tag.category==self.category))

    def serializeTree(self):
        data = self.serialize()
        data['children'] = [child.serializeTree() for child in self.children]
        if len(data['children']) == 1:
            return data['children'][0]
        return data

    def serialize(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'taxonomy': self.taxonomy
        }

    @staticmethod
    def tree():
        cats = {}

        for tag in Tag.query.filter_by(parent_id=None).all():
            if tag.category in cats:
                cats[tag.category].append(tag.serializeTree())
            else:
                cats[tag.category] = [tag.serializeTree()]
        return cats

    def __eq__(self, obj):
        return isinstance(obj, Tag) and obj.id == self.id

    def __repr__(self):
        return '<Tag {}>'.format(self.taxonomy)

    def __hash__(self):
        return hash(self.id)

class Taxonomy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxonomy.id'))
    scans = db.relationship('Scan', secondary='scan_taxonomy')
    children = db.relationship('Taxonomy')

    def serializeTree(self, depth = float('inf')):
        if len(self.children) == 1:
            return self.children[0].serializeTree(depth)

        data = self.serialize()
        if depth > 0:
            data['children'] = [child.serializeTree(depth - 1) for child in self.children]
        else:
            data['children'] = []
        return data

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

    @staticmethod
    def tree():
        return [ tag.serializeTree() for tag in Taxonomy.query.filter_by(parent_id=None).all() ]

    def __repr__(self):
        return '<Taxonomy {}>'.format(self.name)

class ScanPublication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))

class ScanTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))

class ScanTaxonomy(db.Model):
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomy.id'), primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), primary_key=True)

class ScanAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    scan = db.relationship('Scan')
    attachment = db.relationship('Attachment', cascade='all')
