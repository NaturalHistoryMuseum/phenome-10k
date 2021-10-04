from phenome10k.extensions import db
from sqlalchemy.sql import func


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

    # association proxy relationships
    publications = db.relationship('Publication', secondary='scan_publication', backref='scans')
    attachments = db.relationship('Attachment', secondary='scan_attachment', backref='scans', cascade='all')
    tags = db.relationship('Tag', secondary='scan_tag', backref='scans', lazy='select')
    taxonomy = db.relationship('Taxonomy', secondary='scan_taxonomy', backref='scans')

    errors = []

    @property
    def geologic_age(self):
        return [t for t in self.tags if t.category == 'geologic_age']

    @property
    def ontogenic_age(self):
        return [t for t in self.tags if t.category == 'ontogenic_age']

    @property
    def elements(self):
        return [t for t in self.tags if t.category == 'elements']

    @property
    def thumbnail(self):
        return len(self.attachments) > 0 and self.attachments[0]

    def serialize(self, full=True):
        obj = {
            'id': self.id,
            'url_slug': (self.url_slug if self.url_slug else str(self.id)),
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
