from marshmallow import fields

from ._utils import PublicList
from ..extensions import ma
from ..models import File, Attachment


class FileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = File
        include_fk = True
        exclude = ['location', 'owner_id', 'storage_area']


class AttachmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Attachment
        include_fk = True

    id = ma.auto_field()
    name = ma.auto_field()
    file = fields.Nested(FileSchema())
