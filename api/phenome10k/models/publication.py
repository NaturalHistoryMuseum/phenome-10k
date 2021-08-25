from sqlalchemy.sql import func

from phenome10k.extensions import db


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
