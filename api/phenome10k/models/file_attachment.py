import os
import time

import magic
from flask import current_app
from flask.helpers import url_for
from flask_security import current_user
from phenome10k.extensions import db
from sqlalchemy import event
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename


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
        storage_dir = current_app.config['UPLOAD_DIRECTORY'] if storage_area == File.UPLOADS_DIR else \
            current_app.config['MODEL_DIRECTORY'] if storage_area == File.MODELS_DIR else None

        if storage_dir is None:
            raise Exception('No filesystem path is configured for storage area named ' + storage_area)

        return os.path.join(storage_dir, location)

    def get_absolute_path(self):
        """Returns the absolute path on the filesystem for this file"""
        return File.get_absolute_path_for(self.storage_area, self.location)

    def serialize(self, external=False):
        """Returns the url for downloading this file over http"""
        return (
            url_for('files.send_uploads', path=self, _external=external) if self.storage_area == File.UPLOADS_DIR else
            url_for('files.send_models', path=self, _external=external) if self.storage_area == File.MODELS_DIR else
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
