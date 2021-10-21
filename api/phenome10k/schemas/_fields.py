from marshmallow import fields


class PublicList(fields.List):
    def _serialize(self, value, attr, obj, **kwargs):
        value = [v for v in value if v.published]
        return super(PublicList, self)._serialize(value, attr, obj, **kwargs)
