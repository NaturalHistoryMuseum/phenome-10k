from phenome10k.extensions import db


class ScanPublication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))


class ScanTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))


class ScanTaxonomy(db.Model):
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), primary_key=True)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomy.id'), primary_key=True)


class ScanAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    def is_owned_by(self, user):
        """
        Return true if the given user owns this model.
        """
        return self.scan.is_owned_by(user)


class PublicationFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'))
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))

    def is_owned_by(self, user):
        """
        Return true if the given user owns this model.
        """
        return self.publication.is_owned_by(user)
