from phenome10k.extensions import db


class Taxonomy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxonomy.id'))
    gbif = db.Column(db.Boolean, nullable=False, default=True)

    children = db.relationship('Taxonomy')

    def serialize_tree(self, depth=float('inf')):
        """
        Returns a serialized version of this model, with all of its children serialized
        too.

        If this node only has one child, it will use _that_ child's children as its own,
        effectively skipping nodes that are the only child of their parent.
        """
        data = self.serialize()

        if depth > 0:
            data['children'] = [
                child.serialize_tree(depth - 1) for child in self.children
            ]
        else:
            data['children'] = []
        return data

    def serialize(self):
        return {'id': self.id, 'name': self.name}

    @staticmethod
    def tree():
        return [
            tag.serialize_tree()
            for tag in Taxonomy.query.filter_by(parent_id=None).all()
        ]

    def __repr__(self):
        return '<Taxonomy {}>'.format(self.name)
