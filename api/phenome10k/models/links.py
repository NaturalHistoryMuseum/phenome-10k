from phenome10k.extensions import db


class ScanPublication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))

    scan = db.relationship('Scan', backref='scan_publication_ref')
    publication = db.relationship('Publication', backref='scan_publication_ref')


class ScanTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))

    scan = db.relationship('Scan', backref='scan_tag_ref')
    tag = db.relationship('Tag', backref='scan_tag_ref')


class ScanTaxonomy(db.Model):
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), primary_key=True)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomy.id'), primary_key=True)

    scan = db.relationship('Scan', backref='scan_taxonomy_ref')
    taxonomy = db.relationship('Taxonomy', backref='scan_taxonomy_ref')


class ScanAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    scan = db.relationship('Scan', backref='scan_attachment_ref', cascade='all')
    attachment = db.relationship('Attachment', cascade='all')

    def is_owned_by(self, user):
        """ Return true if the given user owns this model """
        return self.scan.is_owned_by(user)


class PublicationFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    publication = db.relationship('Publication', backref='publication_file_ref', cascade='all')
    attachment = db.relationship('Attachment', backref='publication_file_ref', cascade='all')

    def is_owned_by(self, user):
        """ Return true if the given user owns this model """
        return self.publication.is_owned_by(user)
