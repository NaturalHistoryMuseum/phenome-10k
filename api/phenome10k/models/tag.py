from phenome10k.extensions import db


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    taxonomy = db.Column(db.String(250), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tag.id'))

    @property
    def children(self):
        return Tag.query.filter(
            db.and_(Tag.parent_id == self.id, Tag.category == self.category)
        )

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
            'taxonomy': self.taxonomy,
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
