import os
import time

import magic
from flask.helpers import url_for
from flask_login import UserMixin, current_user
from passlib.context import CryptContext
from sqlalchemy import event
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename

from app import db, login, app


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Allow decoding phpasswords, but deprecate all but argon2
cryptCtx = CryptContext(
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
        self.password = cryptCtx.hash(password)

    def check_password(self, password):
        return cryptCtx.verify(password, self.password)

    def password_needs_update(self):
        return cryptCtx.needs_update(self.password)

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


class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gbif_id = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, index=True, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    scientific_name = db.Column(db.String(250), index=True)
    published = db.Column(db.Boolean)
    url_slug = db.Column(db.String(250), index=True, unique=True)
    alt_name = db.Column(db.String(250))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    ctm_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    specimen_id = db.Column(db.String(250))
    specimen_location = db.Column(db.String(250))
    specimen_link = db.Column(db.String(250))
    description = db.Column(db.Text())

    source = db.relationship('File', foreign_keys='Scan.file_id', cascade='all')
    ctm = db.relationship('File', foreign_keys='Scan.ctm_id', cascade='all')
    publications = db.relationship('Publication', secondary='scan_publication', backref='scans')
    attachments = db.relationship('Attachment', secondary='scan_attachment', cascade='all')
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

    @property
    def thumbnail(self):
        return len(self.attachments) > 0 and self.attachments[0]

    def serialize(self, full=True):
        obj = {
            'id': self.id,
            'url_slug': '/' + (self.url_slug if self.url_slug else str(self.id)),
            'thumbnail': self.thumbnail and self.thumbnail.file.serialize(),
            'scientific_name': self.scientific_name
        }

        if full:
            obj.update({
                'ctm': self.ctm and self.ctm.serialize(),
                'source': self.source and self.source.serialize(),
                'attachments': [a.serialize() for a in self.attachments],
                'gbif_id': self.gbif_id,
                'published': self.published,
                'alt_name': self.alt_name,
                'specimen_id': self.specimen_id,
                'specimen_location': self.specimen_location,
                'specimen_link': self.specimen_link,
                'description': self.description,
                'created': self.date_created.isoformat(),
                'author': self.author.name,
                'tags': [tag.serialize() for tag in self.tags],
                'publications': [publication.serialize() for publication in self.publications],
                'stills': [still.serialize() for still in self.attachments]
            })

        return obj

    @staticmethod
    def find_by_slug(slug):
        return Scan.query.filter(db.or_(Scan.url_slug == slug, Scan.id == slug)).first()

    def is_owned_by(self, user):
        """ Return true if the given user owns this model """
        return self.author_id == user.id

    def __repr__(self):
        return '<Scan {}>'.format(self.scientific_name)


class File(db.Model):
    UPLOADS_DIR = 'uploads'
    MODELS_DIR = 'models'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    storage_area = db.Column(db.Enum(UPLOADS_DIR, MODELS_DIR), server_default=UPLOADS_DIR)
    date_created = db.Column(db.DateTime, index=True, server_default=func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mime_type = db.Column(db.String(250), nullable=False)
    size = db.Column(db.Integer)

    owner = db.relationship('User')

    @staticmethod
    def from_upload(file_storage, storage_area=UPLOADS_DIR, save=True, owner_id=None):
        """Create a File model from a Werkzeug FileStorage object, and save the file to disk"""
        file = File.from_binary(file_storage.filename, file_storage.stream, storage_area, owner_id)
        if save:
            file_storage.save(file.get_absolute_path())
        return file

    @staticmethod
    def from_binary(filename, stream, storage_area=UPLOADS_DIR, owner_id=None):
        """Create a File model from a string filename and file-like object"""
        mime_type = magic.from_buffer(stream.read(1024), mime=True)
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0)

        return File.from_name(
            filename,
            size=size,
            mime_type=mime_type,
            storage_area=storage_area,
            owner_id=owner_id
        )

    @staticmethod
    def from_name(filename, storage_area=UPLOADS_DIR, mime_type=None, size=None, owner_id=None):
        """Create a File model from a string filename with optional size and mimetype"""

        filedir = time.strftime('%Y/%m/%d')
        basename, ext = os.path.splitext(filename)

        try:
            os.makedirs(
                File.get_absolute_path_for(storage_area, filedir)
            )
        except FileExistsError:
            pass

        location = '/'.join((filedir, secure_filename(filename)))

        n = 1

        while os.path.isfile(File.get_absolute_path_for(storage_area, location)):
            location = '/'.join((filedir, secure_filename(basename) + '-' + str(n) + ext,))
            n += 1

        return File(
            filename=filename,
            location=location,
            owner_id=owner_id or current_user.id,
            mime_type=mime_type,
            size=size,
            storage_area=storage_area
        )

    @staticmethod
    def get_absolute_path_for(storage_area, location):
        """Returns the absolute path on the filesystem for a file"""
        storage_dir = app.config['UPLOAD_DIRECTORY'] if storage_area == File.UPLOADS_DIR else \
            app.config['MODEL_DIRECTORY'] if storage_area == File.MODELS_DIR else None

        if storage_dir is None:
            raise Exception('No filesystem path is configured for storage area named ' + storage_area)

        return os.path.join(storage_dir, location)

    def get_absolute_path(self):
        """Returns the absolute path on the filesystem for this file"""
        return File.get_absolute_path_for(self.storage_area, self.location)

    def serialize(self, external=False):
        """Returns the url for downloading this file over http"""
        return (url_for('send_uploads', path=self, _external=external) if self.storage_area == File.UPLOADS_DIR else
                url_for('send_models', path=self, _external=external) if self.storage_area == File.MODELS_DIR else
                os.path.join('/', self.location))

    def __repr__(self):
        return '<File {}>'.format(self.filename)


@event.listens_for(File, 'after_delete')
def receive_after_delete(mapper, connection, target):
    """Ensure the files get deleted from disk when the record is deleted"""
    try:
        os.remove(target.get_absolute_path())
    except Exception:
        # FIXME log the exception
        pass


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    file = db.relationship(
        'File',
        cascade='all'
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

    def is_owned_by(self, user):
        """ Return true if the given user owns this model """
        return self.publication.is_owned_by(user)


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
            'files': [file.serialize() for file in self.files],
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
    def find_by_slug(slug):
        return Publication.query.filter(db.or_(Publication.url_slug == slug, Publication.id == slug)).first()

    def is_owned_by(self, user):
        """ Return true if the given user owns this model """
        return self.author_id == user.id


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    taxonomy = db.Column(db.String(250), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    scans = db.relationship('Scan', secondary='scan_tag', lazy='dynamic')

    @property
    def children(self):
        return Tag.query.filter(db.and_(Tag.parent_id == self.id, Tag.category == self.category))

    def serialize_tree(self):
        data = self.serialize()
        data['children'] = [child.serialize_tree() for child in self.children]
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
                cats[tag.category].append(tag.serialize_tree())
            else:
                cats[tag.category] = [tag.serialize_tree()]
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

    def serialize_tree(self, depth=float('inf')):
        """
        Returns a serialized version of this model, with all of its children
        serialized too. If this node only has one child, it will use
        _that_ child's children as its own, effectively skipping nodes that
        are the only child of their parent.
        """
        data = self.serialize()

        if depth > 0:
            if len(self.children) == 1:
                data['children'] = self.children[0].serialize_tree(depth)['children']
            else:
                data['children'] = [child.serialize_tree(depth - 1) for child in self.children]
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
        return [tag.serialize_tree() for tag in Taxonomy.query.filter_by(parent_id=None).all()]

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

    def is_owned_by(self, user):
        """ Return true if the given user owns this model """
        return self.scan.is_owned_by(user)


class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(255))
    arguments = db.Column(db.JSON)
    created = db.Column(db.DateTime(), server_default=func.now())

    @staticmethod
    def add(method, *args):
        q = Queue(method=method, arguments=args)
        db.session.add(q)
        db.session.commit()

    @staticmethod
    def get():
        task = Queue.query.order_by('created').first()
        if task is None:
            return None

        method = task.method
        args = task.arguments

        db.session.delete(task)
        db.session.commit()

        return method, args

    @staticmethod
    def read(sleep=1):
        import time
        while True:
            task = Queue.get()
            if task is None:
                time.sleep(sleep)
            else:
                yield task
